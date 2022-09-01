import sys
import time
from datetime import datetime, timedelta

import pytest

from currencycom import constants
from currencycom.client import CandlesticksChartIntervals


class TestKlines:
    values = [1, 59, 99, 101, 500, 999, 1000]

    def test_klines_check_interval_pos(self, client):
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.MINUTE,
                                   limit=10)

        count = 0
        prev_value = None
        for op_time in klines:
            assert op_time[0] % 60000 == 0  # and
            if count > 0:
                assert op_time[0] - prev_value == 60000
            prev_value = op_time[0]
            count += 1

    @pytest.mark.parametrize('limit',
                             [1, 500, 999, 1000])
    def test_get_klines_limits_pos(self, client, limit):
        """
        Проверяем количество лимитов и количество полученных значений
        """
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.MINUTE,
                                   limit=limit)
        assert len(klines) == limit

    @pytest.mark.parametrize('limit',
                             [float('inf'), float('-inf'), -1, 0, 1001,
                              sys.maxsize, -sys.maxsize])
    def test_get_klines_limits_neg(self, client, limit):
        """
        Проверяем количество лимитов и количество полученных значений
        """
        if limit <= 0:
            klines = client.get_klines(symbol='META.',
                                       interval=CandlesticksChartIntervals.
                                       FIFTEEN_MINUTES,
                                       limit=limit)
            assert klines['code'] == -1128
        else:
            with pytest.raises(ValueError):
                client.get_klines(symbol='META.',
                                  interval=CandlesticksChartIntervals.
                                  FIFTEEN_MINUTES,
                                  limit=limit)
