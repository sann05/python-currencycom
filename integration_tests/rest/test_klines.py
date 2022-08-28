from currencycom import constants
from currencycom.client import CandlesticksChartIntervals


class TestKlines:
    #TODO cделать ширину строки 79 символов
    def test_get_klines_max_limit_interval_minute(self, client):
        klines_meta = client.get_klines(symbol='META.', interval=CandlesticksChartIntervals.MINUTE,
                                        limit=constants.CurrencycomConstants.KLINES_MAX_LIMIT)
        assert len(klines_meta) > 0, "We didn't get any information about "
        assert isinstance(klines_meta[0][0],
                          int), "We get wrong information from klines(open time), we should get int"

    def test_get_klines_fiften_minutes_min_stock_limit(self, client):
        klines_nzd_jpy = client.get_klines(symbol="NZD/JPY_LEVERAGE",
                                           interval=CandlesticksChartIntervals.FIFTEEN_MINUTES)
        assert len(klines_nzd_jpy) > 0, f"We didn't get ant information about klines/candlestick NZD/JPY_LEVERAGE"
        assert isinstance(klines_nzd_jpy[0][0],
                          int), "We get wrong information from klines(open time), we should get int"

    def test_get_klines_week_limit_min(self, client):
        klines_nzd_jpy = client.get_klines(symbol="AOS.", interval=CandlesticksChartIntervals.WEEK,
                                           limit=1)
        # Here we get only 1 list,with 6 values, Open time, open, high, low, close, volume
        assert len(klines_nzd_jpy) == 1, f"We didn't get ant information about klines/candlestick NZD/JPY_LEVERAGE"
        assert isinstance(klines_nzd_jpy[0][0],
                          int), "We get wrong information from klines(open time), we should get int"

    def test_get_klines_negative_day(self, client):
        klines = client.get_klines(symbol="TEST", interval=CandlesticksChartIntervals.DAY)
        assert klines['code'] == -1128, "The negative test has problem with klines['code'] == -1128"
