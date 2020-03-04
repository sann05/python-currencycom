import hashlib
import hmac
from datetime import datetime, timedelta
from enum import Enum

import requests


class CurrencyComConstants(object):
    HEADER_API_KEY_NAME = 'X-MBX-APIKEY'
    API_VERSION = 'v1'
    BASE_URL = 'https://api-adapter.backend.currency.com/api/{}/'.format(
        API_VERSION
    )

    AGG_TRADES_MAX_LIMIT = 1000
    KLINES_MAX_LIMIT = 1000
    # Public API Endpoints
    SERVER_TIME_ENDPOINT = BASE_URL + 'time'
    EXCHANGE_INFORMATION_ENDPOINT = BASE_URL + 'exchangeInfo'

    # Market data Endpoints
    ORDER_BOOK_ENDPOINT = BASE_URL + 'depth'
    AGGREGATE_TRADE_LIST_ENDPOINT = BASE_URL + 'aggTrades'
    KLINES_DATA_ENDPOINT = BASE_URL + 'klines'

    MAX_RECV_WINDOW = 60000


class OrderStatus(Enum):
    NEW = 'NEW'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'


class OrderTypes(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'


class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class CandlesticksChartInervals(Enum):
    MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    THIRTY_MINUTES = '30m'
    HOUR = '1h'
    FOUR_HOURS = '4h'
    DAY = '1d'
    WEEK = '1w'


class Client(object):
    """
    This is API for market Currency.com
    Please find documentation by https://exchange.currency.com/api
    """

    def __init__(self, api_key, api_secret, version='v1'):
        self.base_url = CurrencyComConstants.BASE_URL.format(version)
        self.api_key = api_key
        self.api_secret = api_secret

    def _validate_limit(self, limit):
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

    def __validate_recv_window(self, recv_window):
        max_value = CurrencyComConstants.MAX_RECV_WINDOW
        if recv_window > max_value:
            raise ValueError(
                'recvValue cannot be greater than {}. Got {}.'.format(
                    max_value,
                    recv_window
                ))

    def __get_params(self, **kwargs):
        t = int(datetime.now().timestamp() * 1000)
        kwargs = {'timestamp': t, **kwargs}
        body = '&'.join(['{}={}'.format(k, v)
                         for k, v in kwargs.items()
                         if v is not None])
        sign = hmac.new(self.api_secret, bytes(body, 'utf-8'),
                        hashlib.sha256).hexdigest()
        return {'signature': sign, **kwargs}

    def __get_header(self, **kwargs):
        return {
            **kwargs,
            CurrencyComConstants.HEADER_API_KEY_NAME: self.api_key
        }

    def _get(self, *args, **kwargs):
        return requests.get(*args, **kwargs, headers=self.__get_header())

    # General Endpoints

    def get_server_time(self):
        """
        :return: dict object
        Response:
        {
          "serverTime": 1499827319559
        }
        """
        r = requests.get(CurrencyComConstants.SERVER_TIME_ENDPOINT)

        return r.json()

    def get_exchange_info(self):
        """
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
        r = requests.get(CurrencyComConstants.EXCHANGE_INFORMATION_ENDPOINT)
        return r.json()

    # Market Data Endpoints

    def get_order_book(self, symbol, limit=100):
        """
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
        r = requests.get(CurrencyComConstants.ORDER_BOOK_ENDPOINT,
                         params={'symbol': symbol, 'limit': limit})
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
        :param end_time: Timestamp in ms to get aggregate trades from INCLUSIVE.
        :param limit: Default 500; max 1000.
        :return: dict object

        Response:
        [
          {
            "a":1582595833,
            "p":"8980.4",
            "q":"0.0",
            "f":1582595833,
            "l":1582595833,
            "T":1580204505793,
            "m":false,
            "M":true
          }
        ]
        """
        if limit > CurrencyComConstants.AGG_TRADES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                CurrencyComConstants.AGG_TRADES_MAX_LIMIT
            ))

        if start_time and end_time \
                and end_time - start_time > timedelta(hours=1):
            raise ValueError(
                'If both startTime and endTime are sent,'
                ' time between startTime and endTime must be less than 1 hour.'
            )

        params = {'symbol': symbol, 'limit': limit}

        if start_time:
            params['startTime'] = start_time.timestamp() * 1000

        if end_time:
            params['endTime'] = end_time.timestamp() * 1000

        r = requests.get(CurrencyComConstants.AGGREGATE_TRADE_LIST_ENDPOINT,
                         params=params)

        return r.json()

    def get_klines(self, symbol,
                   interval: CandlesticksChartInervals,
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
        if limit > CurrencyComConstants.KLINES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                CurrencyComConstants.KLINES_MAX_LIMIT
            ))

        params = {'symbol': symbol,
                  'interval': interval.value,
                  'limit': limit}

        if start_time:
            params['startTime'] = int(start_time.timestamp() * 1000)
        if end_time:
            params['endTime'] = int(end_time.timestamp() * 1000)
        r = requests.get(CurrencyComConstants.KLINES_DATA_ENDPOINT,
                         params=params)
        return r.json()

    def get_24h_price_change(self):
        pass

    # Account endpoints

    def new_order(self):
        pass

    def cancel_order(self):
        pass

    def get_open_orders(self):
        pass

    def get_account_info(self, recv_window=None):
        """
        :return: dict object
        Response:
        {
          "makerCommission": 15,
          "takerCommission": 15,
          "buyerCommission": 0,
          "sellerCommission": 0,
          "canTrade": true,
          "canWithdraw": true,
          "canDeposit": true,
          "updateTime": 123456789,
          "accountType": "SPOT",
          "balances": [
            {
              "asset": "BTC",
              "free": "4723846.89208129",
              "locked": "0.00000000"
            },
            {
              "asset": "LTC",
              "free": "4763368.68006011",
              "locked": "0.00000000"
            }
          ]
        }
        """
        url = self.base_url + 'account'
        r = self._get(url,
                      params=self.__get_params(recvWindow=recv_window))
        return r.json()

    def get_account_trade_list(self, symbol, start_time=None, end_time=None,
                               limit=500, recv_window=None):
        """
        Get trades for a specific account and symbol.

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
        url = self.base_url + 'myTrades'
        self._validate_limit(limit)
        r = self._get(url,
                      params=self.__get_params(symbol=symbol,
                                               startTime=start_time,
                                               endTime=end_time,
                                               limit=limit,
                                               recvWindow=recv_window),
                      headers=self.__get_header())

        return r.json()
