import asyncio
import json
import logging
import time
import websockets

from random import random
from datetime import datetime
from typing import Optional

from ..client import CurrencycomClient


class ReconnectingWebsocket:
    MAX_RECONNECTS = 5
    MAX_RECONNECT_SECONDS = 60
    MIN_RECONNECT_WAIT = 0.5
    TIMEOUT = 10
    PING_TIMEOUT = 5

    def __init__(self, loop, client, coro):
        self._loop = loop
        self._log = logging.getLogger(__name__)
        self._coro = coro
        self._reconnect_attempts = 0
        self._conn = None
        self._connect_id = None
        self._socket = None
        self._request = {
            "destination": 'ping',
            "correlationId": 0,
            "payload": {}
        }
        self._client: CurrencycomClient = client
        self._last_ping = None

        self._connect()

    def _connect(self):
        self._conn = asyncio.ensure_future(self._run(), loop=self._loop)

    async def _run(self):
        keep_waiting = True
        self._last_ping = time.time()

        async with websockets.connect(self._client.constants.BASE_WSS_URL) as socket:
            self._socket = socket
            self._reconnect_attempts = 0

            try:
                while keep_waiting:
                    if time.time() - self._last_ping > self.PING_TIMEOUT:
                        await self.send_ping()
                    try:
                        evt = await asyncio.wait_for(self._socket.recv(), timeout=self.PING_TIMEOUT)
                    except asyncio.TimeoutError:
                        self._log.debug("Ping timeout in {} seconds".format(self.PING_TIMEOUT))
                        await self.send_ping()
                    except asyncio.CancelledError:
                        self._log.debug("Websocket cancelled error")
                        await self._socket.ping()
                    else:
                        try:
                            evt_obj = json.loads(evt)
                        except ValueError:
                            pass
                        else:
                            await self._coro(evt_obj)
            except websockets.ConnectionClosed:
                keep_waiting = False
                await self._reconnect()
            except Exception as e:
                self._log.debug('Websocket exception:{}'.format(e))
                keep_waiting = False
                await self._reconnect()

    async def _reconnect(self):
        await self.cancel()
        self._reconnect_attempts += 1
        if self._reconnect_attempts < self.MAX_RECONNECTS:
            self._log.debug(f"Websocket reconnecting {self.MAX_RECONNECTS - self._reconnect_attempts} attempts left")
            reconnect_wait = self._get_reconnect_wait(self._reconnect_attempts)
            await asyncio.sleep(reconnect_wait)
            self._connect()
        else:
            self._log.error(f"Websocket could not reconnect after {self._reconnect_attempts} attempts")
            pass

    def _get_reconnect_wait(self, attempts):
        expo = 2 ** attempts
        return round(random() * min(self.MAX_RECONNECT_SECONDS, expo - 1) + 1)

    async def send_message(self, destination, payload, access: Optional[str] = None, retry_count=0):
        if not self._socket:
            if retry_count < 5:
                await asyncio.sleep(1)
                await self.send_message(destination, payload, access, retry_count + 1)
        else:
            self._request["destination"] = destination
            self._request["payload"] = payload
            self._request["correlationId"] += 1

            if access == 'private':
                self._log.error('Private access not implemented')

            message = json.dumps(self._request)
            await self._socket.send(message)

    async def send_ping(self):
        await self.send_message('ping', {}, access='public')
        self._last_ping = time.time()

    async def cancel(self):
        try:
            self._conn.cancel()
        except asyncio.CancelledError:
            pass


class CurrencycomSocketManager:
    """
    A class to manage the websocket connection to Currencycom.

    Use the following methods to subscribe to Currencycom events:
    - subscribe_market_data(symbols)
    """

    def __init__(self):
        """
        Initialise the Currencycom Socket Manager
        """
        self._callback = None
        self._conn: Optional[ReconnectingWebsocket] = None
        self._loop = None
        self._client = None
        self._log = logging.getLogger(__name__)

    @classmethod
    async def create(cls, loop, client, callback):
        self = CurrencycomSocketManager()
        self._loop = loop
        self._client = client
        self._callback = callback
        self._conn = ReconnectingWebsocket(loop, client, self._callback)
        return self

    async def subscribe_market_data(self, symbols: [str]):
        """
        Market data stream
        This subscription produces the following events:
        {
            "status":"OK",
            "Destination":"internal.quote",
            "Payload":{
                "symbolName":"TXN",
                "bid":139.85,
                "bidQty":2500,
                "ofr":139.92000000000002,
                "ofrQty":2500,
                "timestamp":1597850971558
            }
        }
        """
        await self._conn.send_message("marketData.subscribe", {"symbols": symbols}, 'public')