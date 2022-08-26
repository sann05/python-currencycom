class TestExchangeInfo:
    def test_get_exchange_info(self, client):
        exchange_info = client.get_exchange_info()
        assert len(exchange_info[
                       'symbols']) > 0, \
            "We didn't get exchange information - Symbols "
        assert len(exchange_info[
                       'rateLimits']) > 0, \
            "We didn't get exchange information - rateLimits"
        assert isinstance(exchange_info['symbols'], list)
