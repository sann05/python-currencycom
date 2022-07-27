import asyncio
import logging
import threading
from datetime import datetime
from typing import Optional, Any

from .asyncio.websockets import CurrencycomSocketManager
from .client import CurrencycomClient


class CurrencycomHybridClient:
    """
    This is Hybrid (REST + Websockets) API for market Currency.com

    Please find documentation by https://exchange.currency.com/api
    Swagger UI: https://apitradedoc.currency.com/swagger-ui.html#/
    """
    MAX_MARKET_DATA_TIMEOUT = 10 * 1000  # 10 seconds timeout

    def __init__(self, api_key=None, api_secret=None, handler=None, demo=True):
        """
        Initialise the hybrid client

        :param api_key: API key
        :param api_secret: API secret
        :param handler: Your Handler for messages (default is provided)
        :param demo: Use demo API (default is True)
        """
        self._loop = asyncio.get_event_loop()
        self.rest = CurrencycomClient(api_key, api_secret, demo=demo)
        self.csm: Optional[CurrencycomSocketManager] = None
        self.handler = handler
        self.internal_quote_list: [dict] = []
        self.__subscriptions: [str] = []
        self._log = logging.getLogger(__name__)

    def subscribe(self, *args):
        for arg in args:
            if arg not in self.__subscriptions:
                self.__subscriptions.append(arg)

    def __get_last_internal_quote_list_update(self):
        if len(self.internal_quote_list) == 0:
            return None
        last = 0
        for item in self.internal_quote_list:
            last = max(last, item["timestamp"])
        return last

    async def _check_market_data_timeout(self):
        while True:
            last = self.__get_last_internal_quote_list_update()
            if last is not None and datetime.now().timestamp() - last > self.MAX_MARKET_DATA_TIMEOUT:
                self._log.error("Market data timeout")
                await self.csm.subscribe_market_data(self.__subscriptions)
            await asyncio.sleep(self.MAX_MARKET_DATA_TIMEOUT)

    async def __run_wss(self):
        self.csm = await CurrencycomSocketManager.create(self._loop, self.rest, self._handle_evt)
        await self.csm.subscribe_market_data(self.__subscriptions)

        # Check market data timeout
        asyncio.ensure_future(self._check_market_data_timeout(), loop=self._loop)

        self._log.debug("Fully connected to CurrencyCom")

    async def subscribe_depth_market_data(self, symbols: [str]):
        await self.csm.subscribe_depth_market_data(symbols)

    async def subscribe_market_data(self, symbols: [str]):
        await self.csm.subscribe_market_data(symbols)

    async def subscribe_OHLC_market_data(self, intervals: [str], symbols: [str]):
        await self.csm.subscribe_OHLC_market_data(intervals, symbols)

    def __run_async_loop(self):
        self._loop.run_until_complete(self.__run_wss())

    def run(self):
        """
        Run the client in a thread
        """
        t = threading.Thread(target=self.__run_async_loop)
        t.start()

    def __update_internal_quote_list(self, payload: dict[str, Any]):
        if not any(item for item in self.internal_quote_list
                   if item['symbolName'] == payload['symbolName']):
            self.internal_quote_list.append(payload)
            return
        for current in self.internal_quote_list:
            if current['symbolName'] == payload['symbolName']:
                self.internal_quote_list.remove(current)
                self.internal_quote_list.append(payload)
                return

    @property
    def subscriptions(self):
        return self.__subscriptions

    def get_symbol_price(self, symbol: str):
        if not any(item for item in self.internal_quote_list
                   if item['symbolName'] == symbol):
            self._log.warning("There is no {} in working_symbols yet".format(symbol))
            raise ValueError
        else:
            return next(item for item in self.internal_quote_list
                        if item["symbolName"] == symbol)

    async def _handle_evt(self, msg):
        if msg["destination"] == "internal.quote":
            self.__update_internal_quote_list(msg["payload"])
        if self.handler is not None:
            self.handler(msg)

