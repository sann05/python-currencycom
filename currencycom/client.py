import hashlib
import hmac
from datetime import datetime
from enum import Enum

import requests


class CurrencyComConstants(object):
    HEADER_API_KEY_NAME = 'X-MBX-APIKEY'
    BASE_URL = 'https://api-adapter.backend.currency.com/api/{}/'
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

    def __validate_limit(self, limit):
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
        url = self.base_url + 'time'
        r = requests.get(url)

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
        url = self.base_url + 'exchangeInfo'
        r = requests.get(url)
        return r.json()

    # Market Data Endpoints

    def get_depth(self, symbol, limit=100):
        url = self.base_url + 'depth'
        r = self._get(url,
                      params=self.__get_params(symbol=symbol, limit=limit))
        return r.json()

    def get_agg_trades(self, symbol, start_time=None, end_time=None, limit=500):
        url = self.base_url + 'aggTrades'
        # TODO: Validate limit
        # TODO: Timestamp in ms to get aggregate trades from INCLUSIVE.
        # TODO: Timestamp in ms to get aggregate trades from INCLUSIVE.
        # TODO: If both startTime and endTime are sent, time between startTime and endTime must be less than 1 hour.
        r = self._get(url,
                      params=self.__get_params(symbol=symbol,
                                               startTime=start_time,
                                               endTime=end_time,
                                               limit=limit))

        return r.json()

    def get_klines(self, symbol, interval: CandlesticksChartInervals,
                   start_time=None, end_time=None, limit=500):

        url = self.base_url + 'klines'
        r = self._get(url,
                      params=self.__get_params(symbol=symbol,
                                               interval=interval.value,
                                               startTime=start_time,
                                               endTime=end_time,
                                               limit=limit))
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
        self.__validate_limit(limit)
        r = self._get(url,
                      params=self.__get_params(symbol=symbol,
                                               startTime=start_time,
                                               endTime=end_time,
                                               limit=limit,
                                               recvWindow=recv_window),
                      headers=self.__get_header())

        return r.json()
