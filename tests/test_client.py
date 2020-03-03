from unittest.mock import MagicMock

import pytest

from client import Client


class TestClient(object):
    @pytest.fixture(autouse=True)
    def set_client(self, mock_requests):
        self.client = Client('', '')
        self.mock_get = mock_requests

    def test_get_server_time(self, monkeypatch):
        self.client.get_server_time()
        self.mock_get.assert_called_once()

    def test_not_called(self, monkeypatch):
        self.mock_get.assert_not_called()
