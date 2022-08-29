from datetime import datetime, timedelta

import pytest

from currencycom import constants
from currencycom.client import CandlesticksChartIntervals


class TestKlines:
    values = [60, 90, 120, 360, 999, 1000]
    old_dates = [datetime(1970, 1, 1, 0, 33), datetime(1965, 3, 1, 16, 48),
                 datetime(1945, 9, 1, 6, 55)]

    def test_get_klines_max_limit_interval_minute(self, client):
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.
                                   MINUTE,
                                   limit=constants.CurrencycomConstants.
                                   KLINES_MAX_LIMIT)
        assert len(klines) > 0, "We didn't get any information about "
        assert isinstance(klines, list)
        assert isinstance(klines[0][0],
                          int), "We get wrong information " \
                                "from klines(open time), we should get int"
        assert all(isinstance(i, list) for i in klines)

    def test_get_klines_fiften_minutes_min_stock_limit(self, client):
        klines = client.get_klines(symbol="NZD/JPY_LEVERAGE",
                                   interval=CandlesticksChartIntervals.
                                   FIFTEEN_MINUTES)
        assert len(
            klines) > 0, f"We didn't get ant information " \
                         f"about klines/candlestick NZD/JPY_LEVERAGE"
        assert isinstance(klines, list)
        assert isinstance(klines[0][0],
                          int), "We get wrong information " \
                                "from klines(open time), we should get int"
        assert all(isinstance(i, list) for i in klines)

    def test_get_klines_week_limit_min(self, client):
        klines = client.get_klines(symbol="AOS.",
                                   interval=CandlesticksChartIntervals.
                                   WEEK,
                                   limit=1)
        assert len(
            klines) == 1, f"We didn't get ant information " \
                          f"about klines/candlestick NZD/JPY_LEVERAGE"
        assert isinstance(klines[0][0],
                          int), "We get wrong information " \
                                "from klines(open time), we should get int"
        assert isinstance(klines, list)
        assert all(isinstance(i, list) for i in klines)

    def test_get_klines_negative_symbol(self, client):
        klines = client.get_klines(symbol="TEST",
                                   interval=CandlesticksChartIntervals.DAY)
        assert klines[
                   'code'] == -1128, "The negative test has problem " \
                                     "with klines['code'] == -1128"
        assert 'Invalid symbol:' in klines['msg']

    def test_get_klines_negative_limit_minus(self, client):
        klines = client.get_klines(symbol="META.",
                                   interval=CandlesticksChartIntervals.HOUR,
                                   limit=-500)
        assert klines['code'] == -1128, "The test has problem with -500 limit"
        assert klines['msg'] == 'Invalid limit parameter'

    def test_get_klines_negative_limit_float(self, client):
        klines = client.get_klines(symbol="META.",
                                   interval=CandlesticksChartIntervals.MINUTE,
                                   limit=400.5)
        assert klines['code'] == -1128, "The test has problem with -500 limit"
        assert klines['msg'] == 'Combination of parameters invalid'

    def test_get_klines_negative_limit_str(self, client):
        with pytest.raises(TypeError):
            client.get_klines(symbol='META.',
                              interval=CandlesticksChartIntervals.
                              FIFTEEN_MINUTES, limit='ups')

    def test_get_klines_negative_limit_more_max(self, client):
        with pytest.raises(ValueError):
            client.get_agg_trades(symbol='EUR/USD_LEVERAGE', limit=1001)

    def test_get_klines_negative_with_interval(self, client):
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.
                                   THIRTY_MINUTES, )

    @pytest.mark.parametrize('minutes', values)
    def test_start_time_in_future(self, client, minutes):
        dttm_now_plus = datetime.now() + timedelta(minutes=minutes)
        klines = client.get_klines(symbol='EUR/USD_LEVERAGE',
                                   interval=CandlesticksChartIntervals.
                                   FIVE_MINUTES,
                                   start_time=dttm_now_plus)
        assert len(klines) == 0
