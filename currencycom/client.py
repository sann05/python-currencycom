import hashlib
import hmac
from datetime import datetime, timedelta
from enum import Enum

import requests
from deprecated import deprecated
from requests.models import RequestEncodingMixin

from .constants import CurrencycomConstants


class OrderStatus(Enum):
    NEW = 'NEW'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'


class OrderType(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP = 'STOP'


class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class CandlesticksChartIntervals(Enum):
    MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    THIRTY_MINUTES = '30m'
    HOUR = '1h'
    FOUR_HOURS = '4h'
    DAY = '1d'
    WEEK = '1w'


class TimeInForce(Enum):
    GTC = 'GTC'


class ExpireTimestamp(Enum):
    DEFAULT = 0
    GTC = 'GTC'
    FOK = 'FOK'


class NewOrderResponseType(Enum):
    ACK = 'ACK'
    RESULT = 'RESULT'
    FULL = 'FULL'


class CurrencycomClient:
    """
    This is API for market Currency.com
    Please find documentation by https://exchange.currency.com/api
    Swagger UI: https://apitradedoc.currency.com/swagger-ui.html#/
    """

    def __init__(self, api_key, api_secret, demo=False):
        self.api_key = api_key
        self.api_secret = bytes(api_secret, 'utf-8')
        self.demo = demo
        self.constants = CurrencycomConstants(demo=demo)

    @staticmethod
    def _validate_limit(limit):
        max_limit = 1000
        valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
        if limit > max_limit:
            raise ValueError('Limit {} more than max limit: {}'.format(
                limit, max_limit
            ))
        if limit not in valid_limits:
            raise ValueError('Limit {} not among acceptable values: {}'.format(
                limit, valid_limits
            ))

    @staticmethod
    def _to_epoch_milliseconds(dttm: datetime):
        if dttm:
            return int(dttm.timestamp() * 1000)
        else:
            return dttm

    @staticmethod
    def _validate_new_order_resp_type(
            new_order_resp_type: NewOrderResponseType,
            order_type: OrderType
    ):
        if new_order_resp_type == NewOrderResponseType.ACK:
            raise ValueError('ACK mode no more available')

        if order_type == OrderType.MARKET:
            if new_order_resp_type not in [NewOrderResponseType.RESULT,
                                           NewOrderResponseType.FULL]:
                raise ValueError(
                    "new_order_resp_type for MARKET order can be only RESULT"
                    f"or FULL. Got {new_order_resp_type.value}")
        elif order_type == OrderType.LIMIT:
            if new_order_resp_type != NewOrderResponseType.RESULT:
                raise ValueError(
                    "new_order_resp_type for LIMIT order can be only RESULT."
                    f" Got {new_order_resp_type.value}")

    def _validate_recv_window(self, recv_window):
        max_value = self.constants.RECV_WINDOW_MAX_LIMIT
        if recv_window and recv_window > max_value:
            raise ValueError(
                'recvValue cannot be greater than {}. Got {}.'.format(
                    max_value,
                    recv_window
                ))

    def _get_params_with_signature(self, **kwargs):
        t = self._to_epoch_milliseconds(datetime.now())
        kwargs['timestamp'] = t
        # pylint: disable=no-member
        body = RequestEncodingMixin._encode_params(kwargs)
        sign = hmac.new(self.api_secret, bytes(body, 'utf-8'),
                        hashlib.sha256).hexdigest()
        return {'signature': sign, **kwargs}

    def _get_header(self, **kwargs):
        return {
            **kwargs,
            self.constants.HEADER_API_KEY_NAME: self.api_key
        }

    def _get(self, url, **kwargs):
        return requests.get(url,
                            params=self._get_params_with_signature(**kwargs),
                            headers=self._get_header())

    def _post(self, url, **kwargs):
        return requests.post(url,
                             params=self._get_params_with_signature(**kwargs),
                             headers=self._get_header())

    def _delete(self, url, **kwargs):
        return requests.delete(url,
                               params=self._get_params_with_signature(
                                   **kwargs),
                               headers=self._get_header())

    def get_account_info(self,
                         show_zero_balance: bool = False,
                         recv_window: int = None):
        """
        Get current account information

        :param show_zero_balance: will or will not show accounts with zero
        balances. Default value False
        :param recv_window: the value cannot be greater than 60000
        Default value 5000
        :return: dict object
        Response:
        {
            "makerCommission":0.20,
            "takerCommission":0.20,
            "buyerCommission":0.20,
            "sellerCommission":0.20,
            "canTrade":true,
            "canWithdraw":true,
            "canDeposit":true,
            "updateTime":1586935521,
            "balances":[
                {
                    "accountId":"2376104765040206",
                    "collateralCurrency":true,
                    "asset":"BYN",
                    "free":0.0,
                    "locked":0.0,
                    "default":false
                },
                {
                    "accountId":"2376109060084932",
                    "collateralCurrency":true,
                    "asset":"USD",
                    "free":515.59092523,
                    "locked":0.0,
                    "default":true
                }
            ]
        }
        """
        self._validate_recv_window(recv_window)
        r = self._get(self.constants.ACCOUNT_INFORMATION_ENDPOINT,
                      showZeroBalance=show_zero_balance,
                      recvWindow=recv_window)
        return r.json()

    def get_agg_trades(self, symbol,
                       start_time: datetime = None,
                       end_time: datetime = None,
                       limit=500):
        """
        Get compressed, aggregate trades. Trades that fill at the same time,
        from the same order, with the same price will have the quantity
        aggregated. If both startTime and endTime are sent, time between
        startTime and endTime must be less than 1 hour.

        :param symbol:
        :param start_time: Timestamp in ms to get aggregate trades from
        INCLUSIVE.
        :param end_time: Timestamp in ms to get aggregate trades from INCLUSIVE
        :param limit: Default 500; max 1000.
        :return: dict object

        Response:
        [
          {
            "a":1582595833, // Aggregate tradeId
            "p":"8980.4", // Price
            "q":"0.0", // Quantity (should be ignored)
            "T":1580204505793, // Timestamp
            "m":false, // Was the buyer the maker
          }
        ]
        """
        if limit > self.constants.AGG_TRADES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                self.constants.AGG_TRADES_MAX_LIMIT
            ))

        if start_time and end_time \
                and end_time - start_time > timedelta(hours=1):
            raise ValueError(
                'If both startTime and endTime are sent,'
                ' time between startTime and endTime must be less than 1 hour.'
            )

        params = {'symbol': symbol, 'limit': limit}

        if start_time:
            params['startTime'] = self._to_epoch_milliseconds(start_time)

        if end_time:
            params['endTime'] = self._to_epoch_milliseconds(end_time)

        r = requests.get(self.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
                         params=params)

        return r.json()

    def close_trading_position(self, position_id, recv_window=None):
        """
        Close an active leverage trade.

        :param position_id:
        :param recv_window: The value cannot be greater than 60000.
        :return: dict object

        Response example:
        Example:
        {
            "request": [
                {
                "id": 242057,
                "accountId": 2376109060084932,
                "instrumentId": "45076691096786116",
                "rqType": "ORDER_NEW",
                "state": "PROCESSED",
                "createdTimestamp": 1587031306969
                }
            ]
        }
        """
        self._validate_recv_window(recv_window)

        r = self._post(
            self.constants.CLOSE_TRADING_POSITION_ENDPOINT,
            positionId=position_id,
            recvWindow=recv_window
        )
        return r.json()

    def get_order_book(self, symbol, limit=100):
        """
        Order book

        :param symbol:
        :param limit: Default 100; max 1000.
          Valid limits:[5, 10, 20, 50, 100, 500, 1000, 5000]
        :return: dict object
        Response:
        {
          "lastUpdateId": 1027024,
          "asks": [
            [
              "4.00000200",  // PRICE
              "12.00000000"  // QTY
            ]
          ],
          "bids": [
            [
              "4.00000000",   // PRICE
              "431.00000000"  // QTY
            ]
          ]
          }
        """
        self._validate_limit(limit)
        r = requests.get(self.constants.ORDER_BOOK_ENDPOINT,
                         params={'symbol': symbol, 'limit': limit})
        return r.json()

    def get_exchange_info(self):
        """
        Current exchange trading rules and symbol information.

        :return: dict object
        Response:
        {
          "timezone": "UTC",
          "serverTime": 1577178958852,
          "rateLimits": [
            {
              //These are defined in the `ENUM definitions`
              // section under `Rate Limiters (rateLimitType)`.
              //All limits are optional
            }
          ],
            "symbols": [
                {
                    "symbol": "DPW",
                    "name":"Deutsche Post",
                    "status": "TRADING",
                    "baseAsset": "DPW",
                    "baseAssetPrecision": 3,
                    "quoteAsset": "EUR",
                    "quotePrecision": 3,
                    "orderTypes": [
                        "LIMIT",
                        "MARKET"
                    ],
                    "icebergAllowed": false,
                    "filters": [],
                    "marginTradingAllowed": true,
                    "spotTradingAllowed": true
                },
          ]
        }
        """
        r = requests.get(self.constants.EXCHANGE_INFORMATION_ENDPOINT)
        return r.json()

    def get_klines(self, symbol,
                   interval: CandlesticksChartIntervals,
                   start_time: datetime = None,
                   end_time: datetime = None,
                   limit=500):
        """
        Kline/candlestick bars for a symbol. Klines are uniquely identified
        by their open time.

        If startTime and endTime are not sent, the most recent klines are
        returned.
        :param symbol:
        :param interval:
        :param start_time:
        :param end_time:
        :param limit:Default 500; max 1000.
        :return: dict object

        Response:
        [
          [
            1499040000000,      // Open time
            "0.01634790",       // Open
            "0.80000000",       // High
            "0.01575800",       // Low
            "0.01577100",       // Close
            "148976.11427815"   // Volume.
          ]
        ]
        """
        if limit > self.constants.KLINES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                self.constants.KLINES_MAX_LIMIT
            ))

        params = {'symbol': symbol,
                  'interval': interval.value,
                  'limit': limit}

        if start_time:
            params['startTime'] = self._to_epoch_milliseconds(start_time)
        if end_time:
            params['endTime'] = self._to_epoch_milliseconds(end_time)
        r = requests.get(self.constants.KLINES_DATA_ENDPOINT,
                         params=params)
        return r.json()

    def get_leverage_settings(self, symbol, recv_window=None):
        """
        General leverage settings can be seen.

        :param symbol: Only leverage symbols allowed here
        (AAPL = AAPL_LEVERAGE)
        :param recv_window:
        :return: dict object

        Example:
        {
            "values": [
                2,
                5,
                10,
                20,
                50,
                100
            ], // the possible leverage sizes;
            "value": 20 // depicts a default leverage size which will be set in
            case you don’t mention the ‘leverage’ parameter in the
            corresponding requests.
        }
        """
        self._validate_recv_window(recv_window)

        r = self._get(
            self.constants.LEVERAGE_SETTINGS_ENDPOINT,
            symbol=symbol,
            recvWindow=recv_window
        )
        return r.json()

    def get_account_trade_list(self, symbol,
                               start_time: datetime = None,
                               end_time: datetime = None,
                               limit=500,
                               recv_window=None):
        """
        Get trades for a specific account and symbol.

        :param symbol: Symbol - In order to receive orders within an ‘exchange’
        trading mode ‘symbol’ parameter value from the exchangeInfo endpoint:
        ‘BTC%2FUSD’.
        In order to mention the right symbolLeverage it should be checked with
        the ‘symbol’ parameter value from the exchangeInfo endpoint. In case
        ‘symbol’ has currencies in its name then the following format should be
        used: ‘BTC%2FUSD_LEVERAGE’. In case ‘symbol’ has only an asset name
        then for the leverage trading mode the following format is correct:
         ‘Oil%20-%20Brent.’
        :param start_time:
        :param end_time:
        :param limit: 	Default Value: 500; Max Value: 1000.
        :param recv_window: The value cannot be greater than 60000.
        Default value : 5000
        :return: dict object
        Response:
        [
          {
            "symbol": "BTC/USD",
            "orderId": "100234",
            "orderListId": -1,
            "price": "4.00000100",
            "qty": "12.00000000",
            "quoteQty": "48.000012",
            "commission": "10.10000000",
            "commissionAsset": "BTC",
            "time": 1499865549590,
            "isBuyer": true,
            "isMaker": false
          }
        ]
        """
        self._validate_limit(limit)
        self._validate_recv_window(recv_window)

        params = {'symbol': symbol, 'limit': limit, 'recvWindow': recv_window}

        if start_time:
            params['startTime'] = self._to_epoch_milliseconds(start_time)

        if end_time:
            params['endTime'] = self._to_epoch_milliseconds(end_time)

        r = self._get(self.constants.ACCOUNT_TRADE_LIST_ENDPOINT,
                      **params)

        return r.json()

    def get_open_orders(self, symbol=None, recv_window=None):
        """
        Get all open orders on a symbol. Careful when accessing this with no
        symbol.
        If the symbol is not sent, orders for all symbols will be returned in
        an array.

        :param symbol: Symbol - In order to receive orders within an ‘exchange’
        trading mode ‘symbol’ parameter value from the exchangeInfo endpoint:
        ‘BTC%2FUSD’.
        In order to mention the right symbolLeverage it should be checked with
        the ‘symbol’ parameter value from the exchangeInfo endpoint. In case
        ‘symbol’ has currencies in its name then the following format should be
        used: ‘BTC%2FUSD_LEVERAGE’. In case ‘symbol’ has only an asset name
        then for the leverage trading mode the following format is correct:
         ‘Oil%20-%20Brent.’
        :param recv_window: The value cannot be greater than 60000.
        :return: dict object

        Response:
        [
          {
            "symbol": "LTC/BTC",
            "orderId": "1",
            "orderListId": -1,
            "clientOrderId": "myOrder1",
            "price": "0.1",
            "origQty": "1.0",
            "executedQty": "0.0",
            "cummulativeQuoteQty": "0.0",
            "status": "NEW",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0.0",
            "time": 1499827319559,
            "updateTime": 1499827319559,
            "isWorking": true,
            "origQuoteOrderQty": "0.000000"
          }
        ]
        """

        self._validate_recv_window(recv_window)

        r = self._get(self.constants.CURRENT_OPEN_ORDERS_ENDPOINT,
                      symbol=symbol,
                      recvWindow=recv_window)
        return r.json()

    def new_order(self,
                  symbol,
                  side: OrderSide,
                  order_type: OrderType,
                  quantity: float,
                  account_id: str = None,
                  expire_timestamp: datetime = None,
                  guaranteed_stop_loss: bool = False,
                  stop_loss: float = None,
                  take_profit: float = None,
                  leverage: int = None,
                  price: float = None,
                  new_order_resp_type: NewOrderResponseType
                  = NewOrderResponseType.RESULT,
                  recv_window=None
                  ):
        """
        To create a market or limit order in the exchange trading mode, and
        market, limit or stop order in the leverage trading mode.
        Please note that to open an order within the ‘leverage’ trading mode
        symbolLeverage should be used and additional accountId parameter should
        be mentioned in the request.
        :param symbol: In order to mention the right symbolLeverage it should
        be checked with the ‘symbol’ parameter value from the exchangeInfo
        endpoint. In case ‘symbol’ has currencies in its name then the
        following format should be used: ‘BTC%2FUSD_LEVERAGE’. In case
        ‘symbol’ has only an asset name then for the leverage trading mode the
        following format is correct: ‘Oil%20-%20Brent’.
        :param side:
        :param order_type:
        :param quantity:
        :param account_id:
        :param expire_timestamp:
        :param guaranteed_stop_loss:
        :param stop_loss:
        :param take_profit:
        :param leverage:
        :param price: Required for LIMIT orders
        :param new_order_resp_type: newOrderRespType in the exchange trading
        mode for MARKET order RESULT or FULL can be mentioned. MARKET order
        type default to FULL. LIMIT order type can be only RESULT. For the
        leverage trading mode only RESULT is available.
        :param recv_window: The value cannot be greater than 60000.
        :return: dict object

        Response RESULT:
        {
           "clientOrderId" : "00000000-0000-0000-0000-00000002cac8",
           "status" : "FILLED",
           "cummulativeQuoteQty" : null,
           "executedQty" : "0.001",
           "type" : "MARKET",
           "transactTime" : 1577446511069,
           "origQty" : "0.001",
           "symbol" : "BTC/USD",
           "timeInForce" : "FOK",
           "side" : "BUY",
           "price" : "7173.6186",
           "orderId" : "00000000-0000-0000-0000-00000002cac8"
        }
        Response FULL:
        {
          "orderId" : "00000000-0000-0000-0000-00000002ca43",
          "price" : "7183.3881",
          "clientOrderId" : "00000000-0000-0000-0000-00000002ca43",
          "side" : "BUY",
          "cummulativeQuoteQty" : null,
          "origQty" : "0.001",
          "transactTime" : 1577445603997,
          "type" : "MARKET",
          "executedQty" : "0.001",
          "status" : "FILLED",
          "fills" : [
           {
             "price" : "7169.05",
             "qty" : "0.001",
             "commissionAsset" : "dUSD",
             "commission" : "0"
           }
          ],
          "timeInForce" : "FOK",
          "symbol" : "BTC/USD"
        }
        """
        self._validate_recv_window(recv_window)
        self._validate_new_order_resp_type(new_order_resp_type, order_type)

        if order_type == OrderType.LIMIT:
            if not price:
                raise ValueError('For LIMIT orders price is required or '
                                 f'should be greater than 0. Got {price}')

        expire_timestamp_epoch = self._to_epoch_milliseconds(expire_timestamp)

        r = self._post(
            self.constants.ORDER_ENDPOINT,
            accountId=account_id,
            expireTimestamp=expire_timestamp_epoch,
            guaranteedStopLoss=guaranteed_stop_loss,
            leverage=leverage,
            newOrderRespType=new_order_resp_type.value,
            price=price,
            quantity=quantity,
            recvWindow=recv_window,
            side=side.value,
            stopLoss=stop_loss,
            symbol=symbol,
            takeProfit=take_profit,
            type=order_type.value,
        )
        return r.json()

    def cancel_order(self, symbol,
                     order_id,
                     recv_window=None):
        """
        Cancel an active order within exchange and leverage trading modes.

        :param symbol:
        :param order_id:
        :param recv_window: The value cannot be greater than 60000.
        :return: dict object

        Response:
        {
          "symbol": "LTC/BTC",
          "origClientOrderId": "myOrder1",
          "orderId": "4",
          "orderListId": -1,
          "clientOrderId": "cancelMyOrder1",
          "price": "2.00000000",
          "origQty": "1.00000000",
          "executedQty": "0.00000000",
          "cummulativeQuoteQty": "0.00000000",
          "status": "CANCELED",
          "timeInForce": "GTC",
          "type": "LIMIT",
          "side": "BUY"
        }
        """

        self._validate_recv_window(recv_window)

        r = self._delete(
            self.constants.ORDER_ENDPOINT,
            symbol=symbol,
            orderId=order_id,
            recvWindow=recv_window
        )
        return r.json()

    def get_24h_price_change(self, symbol=None):
        """
        24-hour rolling window price change statistics. Careful when accessing
        this with no symbol.
        If the symbol is not sent, tickers for all symbols will be returned in
        an array.
        :param symbol:
        :return: dict object

        Response:
        {
          "symbol": "LTC/USD",
          "priceChange": "0.88",
          "priceChangePercent": "1.49",
          "weightedAvgPrice": "59.29",
          "prevClosePrice": "58.37",
          "lastPrice": "59.25",
          "lastQty": "220.0",
          "bidPrice": "59.25",
          "askPrice": "59.32",
          "openPrice": "58.37",
          "highPrice": "61.39",
          "lowPrice": "58.37",
          "volume": "22632",
          "quoteVolume": "440.0",
          "openTime": 1580169600000,
          "closeTime": 1580205307222,
          "firstId": 0,
          "lastId": 0,
          "count": 0
        }

        OR

        {
          "symbol": "LTC/USD",
          "priceChange": null,
          "priceChangePercent": null,
          "weightedAvgPrice": "59.29",
          "prevClosePrice": null,
          "lastPrice": "59.23",
          "lastQty": "220.0",
          "bidPrice": "59.23",
          "askPrice": "59.35",
          "openPrice": null,
          "highPrice": null,
          "lowPrice": null,
          "volume": null,
          "quoteVolume": "432.18",
          "openTime": 0,
          "closeTime": 0,
          "firstId": 0,
          "lastId": 0,
          "count": 0
        }
        """
        r = requests.get(self.constants.PRICE_CHANGE_24H_ENDPOINT,
                         params={'symbol': symbol} if symbol else {})
        return r.json()

    def get_server_time(self):
        """
        Test connectivity to the API and get the current server time.

        :return: dict object
        Response:
        {
          "serverTime": 1499827319559
        }
        """
        r = requests.get(self.constants.SERVER_TIME_ENDPOINT)

        return r.json()

    def get_trading_positions(self, recv_window=None):
        """

        :param recv_window:recvWindow cannot be greater than 60000
        Default value : 5000
        :return: dict object
        Example:
        {
            "positions": [
                {
                    "accountId": 2376109060084932,
                    "id": "00a02503-0079-54c4-0000-00004067006b",
                    "instrumentId": "45076691096786116",
                    "orderId": "00a02503-0079-54c4-0000-00004067006a",
                    "openQuantity": 0.01,
                    "openPrice": 6734.4,
                    "closeQuantity": 0.0,
                    "closePrice": 0,
                    "takeProfit": 7999.15,
                    "stopLoss": 5999.15,
                    "guaranteedStopLoss": false,
                    "rpl": 0,
                    "rplConverted": 0,
                    "swap": -0.00335894,
                    "swapConverted": -0.00335894,
                    "fee": -0.050508,
                    "dividend": 0,
                    "margin": 0.5,
                    "state": "ACTIVE",
                    "currency": "USD",
                    "createdTimestamp": 1586953061455,
                    "openTimestamp": 1586953061243,
                    "cost": 33.73775,
                    "symbol": “BTC/USD_LEVERAGE”
                },
                .....
            ]
        }
        """
        self._validate_recv_window(recv_window)
        r = self._get(
            self.constants.TRADING_POSITIONS_ENDPOINT,
            recvWindow=recv_window
        )
        return r.json()

    def update_trading_position(self,
                                position_id,
                                stop_loss: float = None,
                                take_profit: float = None,
                                guaranteed_stop_loss=False,
                                recv_window=None):
        """
        To edit current leverage trade by changing stop loss and take profit
        levels.

        :return: dict object
        Example:
        {
            "requestId": 242040,
            "state": “PROCESSED”
        }
        """
        self._validate_recv_window(recv_window)
        r = self._post(
            self.constants.UPDATE_TRADING_POSITION_ENDPOINT,
            positionId=position_id,
            guaranteedStopLoss=guaranteed_stop_loss,
            stopLoss=stop_loss,
            takeProfit=take_profit
        )
        return r.json()

    def get_trading_position_id(self, order_id):
        """
        Returns order's position_id in TradingPositions using its order_id
        If order doesn't exist in TradingPositions will return None

        :param order_id:

        :return: str
        """
        trading_positions = self.get_trading_positions()['positions']
        for item in trading_positions:
            if item["orderId"] == order_id:
                return item["id"]
        return None


@deprecated(version='1.0.0', reason="Renamed the client. Use CurrencycomClient"
                                    " instead")
class Client(CurrencycomClient):
    pass
