import hashlib
import hmac
from datetime import datetime
from enum import Enum

import requests


class CurrencyComConstants(object):
    HEADER_API_KEY_NAME = 'X-MBX-APIKEY'
    BASE_URL = 'https://api-adapter.backend.currency.com/api/{}/'


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

    # General Endpoints

    def get_server_time(self):
        pass

    def get_exchange_info(self):
        url = self.base_url + 'exchangeInfo'
        r = requests.get(url,
                         params=self.__get_params(),
                         headers=self.__get_header())
        return r.json()

    # Market Data Endpoints

    def get_depth(self, symbol, limit=100):
        url = self.base_url + 'depth'
        r = requests.get(url,
                         params=self.__get_params(symbol=symbol, limit=limit),
                         headers=self.__get_header())
        return r.json()

    def get_agg_trades(self, symbol, start_time=None, end_time=None, limit=500):
        url = self.base_url + 'aggTrades'
        # TODO: Validate limit
        # TODO: Timestamp in ms to get aggregate trades from INCLUSIVE.
        # TODO: Timestamp in ms to get aggregate trades from INCLUSIVE.
        # TODO: If both startTime and endTime are sent, time between startTime and endTime must be less than 1 hour.
        r = requests.get(url,
                         params=self.__get_params(symbol=symbol,
                                                  startTime=start_time,
                                                  endTime=end_time,
                                                  limit=limit),
                         headers=self.__get_header())

        return r.json()

    def get_klines(self, symbol, interval: CandlesticksChartInervals,
                   start_time=None, end_time=None, limit=500):

        url = self.base_url + 'klines'
        r = requests.get(url,
                         params=self.__get_params(symbol=symbol,
                                                  interval=interval.value,
                                                  startTime=start_time,
                                                  endTime=end_time,
                                                  limit=limit),
                         headers=self.__get_header())
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

    def get_account_info(self):
        pass

    def get_account_trade_list(self):
        pass
