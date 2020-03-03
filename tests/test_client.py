from unittest.mock import MagicMock

import pytest

from client import Client, CurrencyComConstants


class TestClient(object):
    @pytest.fixture(autouse=True)
    def set_client(self, mock_requests):
        self.client = Client('', '')
        self.mock_get = mock_requests

    def test_not_called(self):
        self.mock_get.assert_not_called()

    def test_get_server_time(self, monkeypatch):
        self.client.get_server_time()
        self.mock_get.assert_called_once_with(
            CurrencyComConstants.SERVER_TIME_ENDPOINT
        )

    def test_get_exchange_info(self):
        self.client.get_exchange_info()
        self.mock_get.assert_called_once_with(
            CurrencyComConstants.EXCHANGE_INFORMATION_ENDPOINT
        )

    def test_get_order_book_default(self, monkeypatch):
        val_lim_mock = MagicMock()
        monkeypatch.setattr(self.client, '_validate_limit', val_lim_mock)
        symbol = 'TEST'
        self.client.get_order_book(symbol)
        self.mock_get.assert_called_once_with(
            CurrencyComConstants.ORDER_BOOK_ENDPOINT,
            params={'symbol': symbol, 'limit': 100}
        )
        val_lim_mock.assert_called_once_with(100)

    def test_get_order_book_with_limit(self, monkeypatch):
        val_lim_mock = MagicMock()
        limit = 500
        monkeypatch.setattr(self.client, '_validate_limit', val_lim_mock)
        symbol = 'TEST'
        self.client.get_order_book(symbol, limit)
        self.mock_get.assert_called_once_with(
            CurrencyComConstants.ORDER_BOOK_ENDPOINT,
            params={'symbol': symbol, 'limit': limit}
        )
        val_lim_mock.assert_called_once_with(limit)
