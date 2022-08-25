from datetime import datetime, timedelta
import pytest
import sys


class TestAggTrades:
    date_values = [
        datetime(1970, 1, 3),
        datetime(1970, 1, 3, 0, 1),
        datetime(2019, 1, 1),
        datetime.now() - timedelta(minutes=1),
        datetime.now()
    ]

    def test_response_corresponds_swagger_schema(self, client):
        resp_keys = ['T', 'a', 'm', 'p', 'q']
        agg_trades = client.get_agg_trades(symbol='EUR/USD_LEVERAGE')
        assert len(agg_trades) > 0
        assert type(agg_trades) is list
        assert all(type(i) is dict for i in agg_trades)
        assert all((trade[key] is not None for key in trade.keys())
                   for trade in agg_trades)
        assert all((key in resp_keys for key in dct.keys())
                   for dct in agg_trades)

    @pytest.mark.parametrize('dttm', date_values)
    def test_start_time(self, client, dttm):
        dttm_ago_ts = dttm.timestamp()
        agg_trades = client.get_agg_trades(
            symbol='EUR/USD_LEVERAGE',
            start_time=dttm
        )
        assert all(dct["T"] / 1000 >= dttm_ago_ts for dct in agg_trades)

    @pytest.mark.parametrize('dttm', date_values)
    def test_end_time(self, client, dttm):
        dttm_ts = dttm.timestamp()
        agg_trades = client.get_agg_trades(
            symbol='EUR/USD_LEVERAGE',
            end_time=dttm
        )
        assert all(dct["T"] / 1000 <= dttm_ts for dct in agg_trades)

    @pytest.mark.parametrize('minutes', [0, 1, 30, 59, 60])
    def test_start_and_end_time(self, client, minutes):
        dttm_start = datetime.now() - timedelta(days=1)
        dttm_start_ts = dttm_start.timestamp()
        dttm_end = dttm_start + timedelta(minutes=minutes)
        dttm_end_ts = dttm_end.timestamp()
        agg_trades = client.get_agg_trades(
            symbol='EUR/USD_LEVERAGE',
            start_time=dttm_start,
            end_time=dttm_end
        )
        assert all(dttm_start_ts <= dct["T"] / 1000 <= dttm_end_ts
                   for dct in agg_trades)

    @pytest.mark.parametrize('limit', [1, 500, 999, 1000])
    def test_limit(self, client, limit):
        agg_trades = client.get_agg_trades(
            symbol='EUR/USD_LEVERAGE',
            limit=limit
        )
        assert len(agg_trades) == limit

    def test_wrong_symbol(self, client):
        agg_trades = client.get_agg_trades(symbol="TEST123")
        assert agg_trades['code'] == -1128 and 'Invalid symbol: ' \
            in agg_trades['msg']

    @pytest.mark.parametrize('seconds', [1, 214748379, 214748380])
    def test_end_time_less_then_start_time(self, client, seconds):
        dttm_start = datetime.now() - timedelta(days=1)
        dttm_end = dttm_start - timedelta(seconds=seconds)
        agg_trades = client.get_agg_trades(
            symbol='EUR/USD_LEVERAGE',
            start_time=dttm_start,
            end_time=dttm_end
        )
        assert agg_trades['code'] == -1128 and \
               agg_trades['msg'] == 'startTime should be less than endTime'

    @pytest.mark.parametrize('dttm', [datetime.now() + timedelta(minutes=1),
                                      datetime(3001, 1, 3)])
    def test_start_time_in_future(self, client, dttm):
        agg_trades = client.get_agg_trades(
            symbol='EUR/USD_LEVERAGE',
            start_time=dttm)
        assert len(agg_trades) == 0

    @pytest.mark.parametrize('old_date', [datetime(1970, 1, 3),
                                          datetime(1970, 1, 3, 0, 0, 1)]
                             )
    def test_end_time_long_time_ago(self, client, old_date):
        agg_trades = client.get_agg_trades(symbol='EUR/USD_LEVERAGE',
                                           end_time=old_date)
        assert len(agg_trades) == 0

    @pytest.mark.parametrize('over_limit_value', [1001, 5000, sys.maxsize])
    def test_limit_is_more_then_maximum(self, client, over_limit_value):
        with pytest.raises(ValueError):
            client.get_agg_trades(symbol='EUR/USD_LEVERAGE',
                                  limit=over_limit_value)

    @pytest.mark.parametrize('wrong_value', [-sys.maxsize, -1, 0, 15.3])
    def test_invalid_limit(self, client, wrong_value):
        agg_trades = client.get_agg_trades(symbol='EUR/USD_LEVERAGE',
                                           limit=wrong_value)
        assert agg_trades['code'] == -1128 and \
               'invalid' in agg_trades['msg'].lower()

    @pytest.mark.parametrize('seconds', [3601, 2147483646, 2147483647])
    def test_start_and_end_time_diff_more_then_an_hour(self, client, seconds):
        with pytest.raises(ValueError):
            dttm_start = datetime.now() - timedelta(days=1)
            dttm_end = dttm_start + timedelta(seconds=seconds)
            client.get_agg_trades(symbol='EUR/USD_LEVERAGE',
                                  start_time=dttm_start,
                                  end_time=dttm_end)
