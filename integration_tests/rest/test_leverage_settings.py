import pytest
import sys


class TestLeverageSettings:

    def test_response_corresponds_swagger_schema(self, client):
        resp_keys = ['value', 'values']
        lev_settings = client.get_leverage_settings(symbol='EUR/USD_LEVERAGE')
        assert len(lev_settings) > 0
        assert type(lev_settings) is dict
        assert all(lev_settings[key] is not None for key
                   in lev_settings.keys())
        assert all(key in resp_keys for key in lev_settings)

    @pytest.mark.parametrize('recv_val', [60001, sys.maxsize])
    def test_recv_window_over_limit(self, client, recv_val):
        with pytest.raises(ValueError):
            client.get_leverage_settings(symbol='EUR/USD_LEVERAGE',
                                         recv_window=recv_val)

    def test_wrong_symbol(self, client):
        lev_settings = client.get_leverage_settings(symbol="TEST123")
        assert lev_settings['code'] == -1128 and 'Invalid symbol: ' \
               in lev_settings['msg']
