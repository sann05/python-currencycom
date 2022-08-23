from unittest.mock import ANY
from unittest.mock import MagicMock

import pytest

from currencycom.client import *


class TestClient(object):
    @pytest.fixture(autouse=True)
    def set_client(self, mock_requests):
        self.client = CurrencycomClient('', '', demo=False)
        self.mock_requests = mock_requests

    def test_not_called(self):
        self.mock_requests.assert_not_called()

    def test_get_server_time(self, monkeypatch):
        self.client.get_server_time()
        self.mock_requests.assert_called_once_with(
            self.client.constants.SERVER_TIME_ENDPOINT
        )

    def test_get_exchange_info(self):
        self.client.get_exchange_info()
        self.mock_requests.assert_called_once_with(
            self.client.constants.EXCHANGE_INFORMATION_ENDPOINT
        )

    def test_get_order_book_default(self, monkeypatch):
        val_lim_mock = MagicMock()
        monkeypatch.setattr(self.client, '_validate_limit', val_lim_mock)
        symbol = 'TEST'
        self.client.get_order_book(symbol)
        self.mock_requests.assert_called_once_with(
            self.client.constants.ORDER_BOOK_ENDPOINT,
            params={'symbol': symbol, 'limit': 100}
        )
        val_lim_mock.assert_called_once_with(100)

    def test_get_order_book_with_limit(self, monkeypatch):
        val_lim_mock = MagicMock()
        limit = 500
        monkeypatch.setattr(self.client, '_validate_limit', val_lim_mock)
        symbol = 'TEST'
        self.client.get_order_book(symbol, limit)
        self.mock_requests.assert_called_once_with(
            self.client.constants.ORDER_BOOK_ENDPOINT,
            params={'symbol': symbol, 'limit': limit}
        )
        val_lim_mock.assert_called_once_with(limit)

    def test_get_agg_trades_default(self):
        symbol = 'TEST'
        self.client.get_agg_trades(symbol)
        self.mock_requests.assert_called_once_with(
            self.client.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
            params={'symbol': symbol, 'limit': 500}
        )

    def test_get_agg_trades_limit_set(self):
        symbol = 'TEST'
        limit = 20
        self.client.get_agg_trades(symbol, limit=limit)
        self.mock_requests.assert_called_once_with(
            self.client.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
            params={'symbol': symbol, 'limit': limit}
        )

    def test_get_agg_trades_max_limit(self):
        symbol = 'TEST'
        limit = self.client.constants.AGG_TRADES_MAX_LIMIT
        self.client.get_agg_trades(symbol, limit=limit)
        self.mock_requests.assert_called_once_with(
            self.client.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
            params={'symbol': symbol, 'limit': limit}
        )

    def test_get_agg_trades_exceed_limit(self):
        symbol = 'TEST'
        limit = self.client.constants.AGG_TRADES_MAX_LIMIT + 1
        with pytest.raises(ValueError):
            self.client.get_agg_trades(symbol, limit=limit)
        self.mock_requests.assert_not_called()

    def test_get_agg_trades_only_start_time_set(self):
        symbol = 'TEST'
        start_time = datetime(2019, 1, 1, 1, 1, 1)
        self.client.get_agg_trades(symbol, start_time=start_time)
        self.mock_requests.assert_called_once_with(
            self.client.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
            params={'symbol': symbol, 'limit': 500,
                    'startTime': start_time.timestamp() * 1000}
        )

    def test_get_agg_trades_only_end_time_set(self):
        symbol = 'TEST'
        end_time = datetime(2019, 1, 1, 1, 1, 1)
        self.client.get_agg_trades(symbol, end_time=end_time)
        self.mock_requests.assert_called_once_with(
            self.client.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
            params={'symbol': symbol, 'limit': 500,
                    'endTime': end_time.timestamp() * 1000}
        )

    def test_get_agg_trades_both_time_set(self):
        symbol = 'TEST'
        start_time = datetime(2019, 1, 1, 1, 1, 1)
        end_time = datetime(2019, 1, 1, 1, 1, 20)
        self.client.get_agg_trades(symbol,
                                   start_time=start_time,
                                   end_time=end_time)
        self.mock_requests.assert_called_once_with(
            self.client.constants.AGGREGATE_TRADE_LIST_ENDPOINT,
            params={'symbol': symbol, 'limit': 500,
                    'startTime': start_time.timestamp() * 1000,
                    'endTime': end_time.timestamp() * 1000}
        )

    def test_get_agg_trades_both_time_set_exceed_max_range(self):
        symbol = 'TEST'
        start_time = datetime(2019, 1, 1, 1, 1, 1)
        end_time = datetime(2019, 1, 1, 2, 2, 20)
        with pytest.raises(ValueError):
            self.client.get_agg_trades(symbol,
                                       start_time=start_time,
                                       end_time=end_time)
        self.mock_requests.assert_not_called()

    def test_get_klines_default(self):
        symbol = 'TEST'
        self.client.get_klines(symbol, CandlesticksChartIntervals.DAY)
        self.mock_requests.assert_called_once_with(
            self.client.constants.KLINES_DATA_ENDPOINT,
            params={'symbol': symbol,
                    'interval': CandlesticksChartIntervals.DAY.value,
                    'limit': 500}
        )

    def test_get_klines_with_limit(self):
        symbol = 'TEST'
        limit = 123
        self.client.get_klines(symbol, CandlesticksChartIntervals.DAY,
                               limit=limit)
        self.mock_requests.assert_called_once_with(
            self.client.constants.KLINES_DATA_ENDPOINT,
            params={'symbol': symbol,
                    'interval': CandlesticksChartIntervals.DAY.value,
                    'limit': limit}
        )

    def test_get_klines_max_limit(self):
        symbol = 'TEST'
        limit = self.client.constants.KLINES_MAX_LIMIT
        self.client.get_klines(symbol, CandlesticksChartIntervals.DAY,
                               limit=limit)
        self.mock_requests.assert_called_once_with(
            self.client.constants.KLINES_DATA_ENDPOINT,
            params={'symbol': symbol,
                    'interval': CandlesticksChartIntervals.DAY.value,
                    'limit': limit}
        )

    def test_get_klines_exceed_max_limit(self):
        symbol = 'TEST'
        limit = self.client.constants.KLINES_MAX_LIMIT + 1
        with pytest.raises(ValueError):
            self.client.get_klines(symbol, CandlesticksChartIntervals.DAY,
                                   limit=limit)
        self.mock_requests.assert_not_called()

    def test_get_klines_with_startTime(self):
        symbol = 'TEST'
        start_date = datetime(2020, 1, 1)
        self.client.get_klines(symbol,
                               CandlesticksChartIntervals.DAY,
                               start_time=start_date)
        self.mock_requests.assert_called_once_with(
            self.client.constants.KLINES_DATA_ENDPOINT,
            params={'symbol': symbol,
                    'interval': CandlesticksChartIntervals.DAY.value,
                    'startTime': int(start_date.timestamp() * 1000),
                    'limit': 500}
        )

    def test_get_klines_with_endTime(self):
        symbol = 'TEST'
        end_time = datetime(2020, 1, 1)
        self.client.get_klines(symbol,
                               CandlesticksChartIntervals.DAY,
                               end_time=end_time)
        self.mock_requests.assert_called_once_with(
            self.client.constants.KLINES_DATA_ENDPOINT,
            params={'symbol': symbol,
                    'interval': CandlesticksChartIntervals.DAY.value,
                    'endTime': int(end_time.timestamp() * 1000),
                    'limit': 500}
        )

    def test_get_klines_with_startTime_and_endTime(self):
        symbol = 'TEST'
        start_time = datetime(2020, 1, 1)
        end_time = datetime(2021, 1, 1)
        self.client.get_klines(symbol,
                               CandlesticksChartIntervals.DAY,
                               start_time=start_time,
                               end_time=end_time)
        self.mock_requests.assert_called_once_with(
            self.client.constants.KLINES_DATA_ENDPOINT,
            params={'symbol': symbol,
                    'interval': CandlesticksChartIntervals.DAY.value,
                    'startTime': int(start_time.timestamp() * 1000),
                    'endTime': int(end_time.timestamp() * 1000),
                    'limit': 500}
        )

    def test_get_24h_price_change_default(self):
        self.client.get_24h_price_change()
        self.mock_requests.assert_called_once_with(
            self.client.constants.PRICE_CHANGE_24H_ENDPOINT,
            params={}
        )

    def test_get_24h_price_change_with_symbol(self):
        symbol = 'TEST'
        self.client.get_24h_price_change(symbol)
        self.mock_requests.assert_called_once_with(
            self.client.constants.PRICE_CHANGE_24H_ENDPOINT,
            params={'symbol': symbol}
        )

    def test_new_order_default_buy(self, monkeypatch):
        post_mock = MagicMock()
        monkeypatch.setattr(self.client, '_post', post_mock)
        symbol = 'TEST'
        side = OrderSide.BUY
        ord_type = OrderType.MARKET
        amount = 1
        self.client.new_order(symbol, side, ord_type, amount)
        post_mock.assert_called_once_with(
            self.client.constants.ORDER_ENDPOINT,
            accountId=None,
            expireTimestamp=None,
            guaranteedStopLoss=False,
            newOrderRespType=ANY,
            price=ANY,
            quantity=amount,
            recvWindow=ANY,
            side=side.value,
            stopLoss=None,
            symbol=symbol,
            takeProfit=None,
            leverage=None,
            type=ord_type.value,
        )

    def test_new_order_default_sell(self, monkeypatch):
        post_mock = MagicMock()
        monkeypatch.setattr(self.client, '_post', post_mock)
        symbol = 'TEST'
        side = OrderSide.BUY
        ord_type = OrderType.MARKET
        amount = 1
        self.client.new_order(symbol, side, ord_type, amount)
        post_mock.assert_called_once_with(
            self.client.constants.ORDER_ENDPOINT,
            accountId=None,
            expireTimestamp=None,
            guaranteedStopLoss=False,
            newOrderRespType=ANY,
            price=ANY,
            quantity=amount,
            recvWindow=ANY,
            side=side.value,
            stopLoss=None,
            symbol=symbol,
            takeProfit=None,
            leverage=None,
            type=ord_type.value,
        )

    def test_new_order_invalid_recv_window(self, monkeypatch):
        symbol = 'TEST'
        side = OrderSide.BUY
        ord_type = OrderType.MARKET
        amount = 1
        with pytest.raises(ValueError):
            self.client.new_order(
                symbol, side, ord_type, amount,
                recv_window=self.client.constants.RECV_WINDOW_MAX_LIMIT + 1)
        self.mock_requests.assert_not_called()

    def test_new_order_default_limit(self, monkeypatch):
        post_mock = MagicMock()
        monkeypatch.setattr(self.client, '_post', post_mock)
        symbol = 'TEST'
        side = OrderSide.BUY
        ord_type = OrderType.LIMIT
        new_order_resp_type = NewOrderResponseType.RESULT
        amount = 1
        price = 1
        self.client.new_order(symbol,
                              side,
                              ord_type,
                              price=price,
                              new_order_resp_type=new_order_resp_type,
                              quantity=amount)
        post_mock.assert_called_once_with(
            self.client.constants.ORDER_ENDPOINT,
            accountId=None,
            expireTimestamp=None,
            guaranteedStopLoss=False,
            newOrderRespType=new_order_resp_type.value,
            price=ANY,
            quantity=amount,
            recvWindow=ANY,
            side=side.value,
            stopLoss=None,
            symbol=symbol,
            takeProfit=None,
            leverage=None,
            type=ord_type.value,
        )

    def test_new_order_incorrect_limit_no_price(self, monkeypatch):
        post_mock = MagicMock()
        monkeypatch.setattr(self.client, '_post', post_mock)
        symbol = 'TEST'
        side = OrderSide.BUY
        ord_type = OrderType.LIMIT
        amount = 1
        with pytest.raises(ValueError):
            self.client.new_order(symbol,
                                  side,
                                  ord_type,
                                  quantity=amount)
        post_mock.assert_not_called()

    @pytest.mark.skip("There is no more time_in_force parameter")
    def test_new_order_incorrect_limit_no_time_in_force(self, monkeypatch):
        post_mock = MagicMock()
        monkeypatch.setattr(self.client, '_post', post_mock)
        symbol = 'TEST'
        side = OrderSide.BUY
        ord_type = OrderType.LIMIT
        amount = 1
        price = 1
        with pytest.raises(ValueError):
            self.client.new_order(symbol,
                                  side,
                                  ord_type,
                                  price=price,
                                  quantity=amount)
        post_mock.assert_not_called()

    def test_cancel_order_default_order_id(self, monkeypatch):
        delete_mock = MagicMock()
        monkeypatch.setattr(self.client, '_delete', delete_mock)
        symbol = 'TEST'
        order_id = 'TEST_ORDER_ID'
        self.client.cancel_order(symbol, order_id)
        delete_mock.assert_called_once_with(
            self.client.constants.ORDER_ENDPOINT,
            symbol=symbol,
            orderId=order_id,
            recvWindow=None
        )

    def test_cancel_order_default_client_order_id(self, monkeypatch):
        delete_mock = MagicMock()
        monkeypatch.setattr(self.client, '_delete', delete_mock)
        symbol = 'TEST'
        order_id = 'TEST_ORDER_ID'
        self.client.cancel_order(symbol, order_id=order_id)
        delete_mock.assert_called_once_with(
            self.client.constants.ORDER_ENDPOINT,
            symbol=symbol,
            orderId=order_id,
            recvWindow=None
        )

    @pytest.mark.skip("order_id param became mandatory")
    def test_cancel_order_default_no_id(self, monkeypatch):
        delete_mock = MagicMock()
        monkeypatch.setattr(self.client, '_delete', delete_mock)
        symbol = 'TEST'
        with pytest.raises(ValueError):
            self.client.cancel_order(symbol)
        delete_mock.assert_not_called()

    def test_cancel_order_invalid_recv_window(self, monkeypatch):
        delete_mock = MagicMock()
        monkeypatch.setattr(self.client, '_delete', delete_mock)
        symbol = 'TEST'
        with pytest.raises(ValueError):
            self.client.cancel_order(
                symbol, 'id',
                recv_window=self.client.constants.RECV_WINDOW_MAX_LIMIT + 1)
        delete_mock.assert_not_called()

    def test_get_open_orders_default(self, monkeypatch):
        get_mock = MagicMock()
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_open_orders()
        get_mock.assert_called_once_with(
            self.client.constants.CURRENT_OPEN_ORDERS_ENDPOINT,
            symbol=None,
            recvWindow=None
        )

    def test_get_open_orders_with_symbol(self, monkeypatch):
        get_mock = MagicMock()
        symbol = 'Test'
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_open_orders(symbol)
        get_mock.assert_called_once_with(
            self.client.constants.CURRENT_OPEN_ORDERS_ENDPOINT,
            symbol=symbol,
            recvWindow=None
        )

    def test_get_open_orders_invalid_recv_window(self):
        with pytest.raises(ValueError):
            self.client.get_open_orders(
                recv_window=self.client.constants.RECV_WINDOW_MAX_LIMIT + 1)
        self.mock_requests.assert_not_called()

    def test_get_account_info_default(self, monkeypatch):
        get_mock = MagicMock()
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_account_info()
        get_mock.assert_called_once_with(
            self.client.constants.ACCOUNT_INFORMATION_ENDPOINT,
            showZeroBalance=False,
            recvWindow=None
        )

    def test_get_account_info_invalid_recv_window(self):
        with pytest.raises(ValueError):
            self.client.get_account_info(
                recv_window=self.client.constants.RECV_WINDOW_MAX_LIMIT + 1)
        self.mock_requests.assert_not_called()

    def test_get_account_trade_list_default(self, monkeypatch):
        get_mock = MagicMock()
        symbol = 'TEST'
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_account_trade_list(symbol)
        get_mock.assert_called_once_with(
            self.client.constants.ACCOUNT_TRADE_LIST_ENDPOINT,
            symbol=symbol,
            limit=500,
            recvWindow=None
        )

    def test_get_account_trade_list_with_start_time(self, monkeypatch):
        get_mock = MagicMock()
        symbol = 'TEST'
        start_time = datetime(2020, 1, 1, 1, 1, 1)
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_account_trade_list(symbol, start_time=start_time)
        get_mock.assert_called_once_with(
            self.client.constants.ACCOUNT_TRADE_LIST_ENDPOINT,
            symbol=symbol,
            limit=500,
            recvWindow=None,
            startTime=start_time.timestamp() * 1000
        )

    def test_get_account_trade_list_with_end_time(self, monkeypatch):
        get_mock = MagicMock()
        symbol = 'TEST'
        end_time = datetime(2020, 1, 1, 1, 1, 1)
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_account_trade_list(symbol, end_time=end_time)
        get_mock.assert_called_once_with(
            self.client.constants.ACCOUNT_TRADE_LIST_ENDPOINT,
            symbol=symbol,
            limit=500,
            recvWindow=None,
            endTime=end_time.timestamp() * 1000
        )

    def test_get_account_trade_list_with_start_and_end_times(self,
                                                             monkeypatch):
        get_mock = MagicMock()
        symbol = 'TEST'
        start_time = datetime(2019, 1, 1, 1, 1, 1)
        end_time = datetime(2020, 1, 1, 1, 1, 1)
        monkeypatch.setattr(self.client, '_get', get_mock)
        self.client.get_account_trade_list(symbol,
                                           start_time=start_time,
                                           end_time=end_time)
        get_mock.assert_called_once_with(
            self.client.constants.ACCOUNT_TRADE_LIST_ENDPOINT,
            symbol=symbol,
            limit=500,
            recvWindow=None,
            startTime=start_time.timestamp() * 1000,
            endTime=end_time.timestamp() * 1000
        )

    def test_get_account_trade_list_incorrect_recv_window(self):
        with pytest.raises(ValueError):
            self.client.get_account_trade_list(
                'TEST',
                recv_window=self.client.constants.RECV_WINDOW_MAX_LIMIT + 1)
        self.mock_requests.assert_not_called()

    def test_get_account_trade_list_incorrect_limit(self):
        with pytest.raises(ValueError):
            self.client.get_account_trade_list(
                'TEST',
                limit=999)
        self.mock_requests.assert_not_called()

    def test__to_epoch_miliseconds_default(self):
        dttm = datetime(1999, 1, 1, 1, 1, 1)
        assert self.client._to_epoch_milliseconds(dttm) \
               == int(dttm.timestamp() * 1000)
