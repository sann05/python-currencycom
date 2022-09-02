class Test24hPriceChange:

    def test_response_corresponds_swagger_schema(self, client):
        resp_keys = [
            'symbol', 'priceChange', 'priceChangePercent',
            'weightedAvgPrice', 'prevClosePrice', 'lastPrice',
            'lastQty', 'bidPrice', 'askPrice',
            'openPrice', 'highPrice', 'lowPrice',
            'volume', 'quoteVolume', 'openTime', 'closeTime'
        ]
        price_changes = client.get_24h_price_change('GBP/USD_LEVERAGE')
        assert type(price_changes) is dict
        assert len(price_changes) > 0
        assert all(dct in resp_keys for dct in price_changes.keys())
        assert all(price_changes[key] is not None for key in
                   price_changes.keys())

    def test_wrong_symbol(self, client):
        price_changes = client.get_24h_price_change(symbol="TEST123")
        assert price_changes['code'] == -1128 and 'symbol not found ' \
               in price_changes['msg']
