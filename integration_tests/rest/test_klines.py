import functools
import itertools
import sys
import time
from datetime import datetime, timedelta
import pytest

from currencycom import constants
from currencycom.client import CandlesticksChartIntervals


class TestKlines:
    values = [1, 59, 99, 101, 500, 999, 1000]

    def test_klines_base_check(self, client):
        klines = client.get_klines(symbol='GOOGL.',
                                   interval=CandlesticksChartIntervals
                                   .MINUTE)
        assert len(klines) > 0
        assert all(len(i) == 6 for i in klines)

    @pytest.mark.parametrize("interval, minutes", [
        (CandlesticksChartIntervals.MINUTE, 1),
        (CandlesticksChartIntervals.FIVE_MINUTES, 5),
        (CandlesticksChartIntervals.FIFTEEN_MINUTES, 15),
        (CandlesticksChartIntervals.THIRTY_MINUTES, 30),
        (CandlesticksChartIntervals.HOUR, 60),
        (CandlesticksChartIntervals.FOUR_HOURS, 240),
        (CandlesticksChartIntervals.DAY, 1440),
        (CandlesticksChartIntervals.WEEK, 10080),
    ])
    def test_klines_check_interval_pos(self, client, interval, minutes):
        klines = client.get_klines(symbol='META.',
                                   interval=interval)
        assert all(val[0] % 60000 == 0 for val in klines)
        assert (klines[i + 1][0] - klines[i][0] == (minutes * 60000) for i in
                range(len(klines) - 1))

    @pytest.mark.parametrize('limit', [1, 500, 999, 1000])
    def test_get_klines_limits_pos(self, client, limit):
        """
        Проверяем количество лимитов и количество полученных значений
        """
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.MINUTE,
                                   limit=limit)
        assert len(klines) == limit

    @pytest.mark.parametrize('limit',
                             [float('inf'), 1001, sys.maxsize])
    def test_get_klines_limits_neg_plus(self, client, limit):
        """
        Проверяем количество лимитов и количество полученных значений
        """
        with pytest.raises(ValueError):
            client.get_klines(symbol='META.',
                              interval=CandlesticksChartIntervals.
                              FIFTEEN_MINUTES,
                              limit=limit)

    @pytest.mark.parametrize('limit',
                             [float('-inf'), -1, 0, -sys.maxsize])
    def test_get_klines_limits_neg_minus(self, client, limit):
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.
                                   FIFTEEN_MINUTES,
                                   limit=limit)
        assert klines['code'] == -1128
