import functools
import itertools
import sys
import time
from datetime import datetime, timedelta
import pytest

from currencycom import constants
from currencycom.client import CandlesticksChartIntervals


class TestKlines:
    date_values = [
        datetime(1970, 1, 3),
        datetime(1970, 1, 3, 0, 1),
        datetime(2019, 1, 1),
        datetime.now() - timedelta(minutes=1),
        datetime.now()
    ]
    values = [1, 59, 99, 101, 500, 999, 1000]

    def test_base_check(self, client):
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
    def test_check_interval_and_accordance_between_get_klines(self, client,
                                                              interval,
                                                              minutes):
        klines = client.get_klines(symbol='ETH/USD_LEVERAGE',
                                   interval=interval)
        assert all(val[0] % 60000 == 0 for val in klines)
        assert (klines[i + 1][0] - klines[i][0] == (minutes * 60000) for i in
                range(len(klines) - 1))

    @pytest.mark.parametrize('limit', [1, 500, 999, 1000])
    def test_check_valid_limits(self, client, limit):
        """
        Positive test
        Check get counts
        Сравниваем что количество запрашиваемых и полученных значений лимита
        равны.
        """
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.MINUTE,
                                   limit=limit)
        assert len(klines) == limit

    @pytest.mark.parametrize('limit',
                             [1001, sys.maxsize])
    def test_check_limits_more_max_limit(self, client, limit):
        """
        Negative test.
        Check values > max limit(1000)
        """
        with pytest.raises(ValueError):
            client.get_klines(symbol='META.',
                              interval=CandlesticksChartIntervals.
                              FIFTEEN_MINUTES,
                              limit=limit)

    @pytest.mark.parametrize('limit',
                             [-1, 0, -sys.maxsize])
    def test_check_limits_less_1(self, client, limit):
        """
        Negative test
        Check values < min limit(1)
        """
        klines = client.get_klines(symbol='META.',
                                   interval=CandlesticksChartIntervals.
                                   FIFTEEN_MINUTES,
                                   limit=limit)
        assert klines['code'] == -1128

    @pytest.mark.parametrize('date_val', date_values)
    def test_start_time_valid(self, client, date_val):
        klines = client.get_klines(symbol='GOOGL.',
                                   interval=CandlesticksChartIntervals.HOUR,
                                   start_time=date_val)
        date_ago_timestamp = date_val.timestamp()
        assert all(date[0] / 1000 >= date_ago_timestamp for date in klines)

    @pytest.mark.parametrize('date_val', date_values)
    def test_end_time_valid(self, client, date_val):
        klines = client.get_klines(symbol='DBK.',
                                   interval=CandlesticksChartIntervals.
                                   FIFTEEN_MINUTES, end_time=date_val)
        date_ago_timestamp = date_val.timestamp()
        assert all(date[0] / 1000 <= date_ago_timestamp for date in klines)

