from unittest.mock import MagicMock

import pytest


@pytest.fixture(scope='function')
def mock_requests(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('requests.get', mock)
    return mock
