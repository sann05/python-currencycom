class CurrencycomConstants(object):
    HEADER_API_KEY_NAME = 'X-MBX-APIKEY'
    API_VERSION = 'v1'

    _BASE_URL = 'https://api-adapter.backend.currency.com/api/{}/'.format(
        API_VERSION
    )
    _DEMO_BASE_URL = 'https://demo-api-adapter.backend.currency.com/api/{}/'.format(
        API_VERSION
    )

    _BASE_WSS_URL = "wss://api-adapter.backend.currency.com/connect"
    _DEMO_BASE_WSS_URL = "wss://demo-api-adapter.backend.currency.com/connect"

    AGG_TRADES_MAX_LIMIT = 1000
    KLINES_MAX_LIMIT = 1000
    RECV_WINDOW_MAX_LIMIT = 60000

    def __init__(self, demo=True):
        self.demo = demo

    @property
    def BASE_URL(self):
        return self._DEMO_BASE_URL if self.demo else self._BASE_URL

    @property
    def BASE_WSS_URL(self):
        return self._DEMO_BASE_WSS_URL if self.demo else self._BASE_WSS_URL

    # Public API Endpoints
    @property
    def SERVER_TIME_ENDPOINT(self):
        return self.BASE_URL + 'time'

    @property
    def EXCHANGE_INFORMATION_ENDPOINT(self):
        return self.BASE_URL + 'exchangeInfo'

    # Market data Endpoints
    @property
    def ORDER_BOOK_ENDPOINT(self):
        return self.BASE_URL + 'depth'

    @property
    def AGGREGATE_TRADE_LIST_ENDPOINT(self):
        return self.BASE_URL + 'aggTrades'

    @property
    def KLINES_DATA_ENDPOINT(self):
        return self.BASE_URL + 'klines'

    @property
    def PRICE_CHANGE_24H_ENDPOINT(self):
        return self.BASE_URL + 'ticker/24hr'

    # Account Endpoints
    @property
    def ACCOUNT_INFORMATION_ENDPOINT(self):
        return self.BASE_URL + 'account'

    @property
    def ACCOUNT_TRADE_LIST_ENDPOINT(self):
        return self.BASE_URL + 'myTrades'

    # Order Endpoints
    @property
    def ORDER_ENDPOINT(self):
        return self.BASE_URL + 'order'

    @property
    def CURRENT_OPEN_ORDERS_ENDPOINT(self):
        return self.BASE_URL + 'openOrders'

    # Leverage Endpoints
    @property
    def CLOSE_TRADING_POSITION_ENDPOINT(self):
        return self.BASE_URL + 'closeTradingPosition'

    @property
    def TRADING_POSITIONS_ENDPOINT(self):
        return self.BASE_URL + 'tradingPositions'

    @property
    def LEVERAGE_SETTINGS_ENDPOINT(self):
        return self.BASE_URL + 'leverageSettings'

    @property
    def UPDATE_TRADING_ORDER_ENDPOINT(self):
        return self.BASE_URL + 'updateTradingOrder'

    @property
    def UPDATE_TRADING_POSITION_ENDPOINT(self):
        return self.BASE_URL + 'updateTradingPosition'
