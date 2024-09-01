from syntrend.utils import filters

from datetime import datetime, timezone

from pytest import mark


@mark.unit
def test_to_timestamp():
    exp_timestamp = 1704067200
    input_datetime = datetime(2024, 1, 1, tzinfo=timezone.utc)
    result = filters.to_timestamp(input_datetime)
    assert result == exp_timestamp, "Generated datetime should convert to timestamp"


@mark.unit
@mark.parametrize("value,result", [
    ("2024-01-01T00:00:00Z", datetime(2024, 1, 1, tzinfo=timezone.utc)),
    ("2024-01-01+00:00", datetime(2024, 1, 1)),
    ("2024-01-01T00:00:00+00:00", datetime(2024, 1, 1, tzinfo=timezone.utc)),
])
def test_to_datetime(value, result):
    returned = filters.to_datetime(value)
    assert returned == result, "Generated datetime should convert to datetime"


@mark.unit
@mark.parametrize("delta,new_time", [
    ("1d", datetime(2024, 1, 2, tzinfo=timezone.utc)),
    ("1H", datetime(2024, 1, 1, hour=1, tzinfo=timezone.utc)),
    ("1M", datetime(2024, 1, 1, minute=1, tzinfo=timezone.utc)),
    ("1S", datetime(2024, 1, 1, second=1, tzinfo=timezone.utc)),
    ("1d 5H", datetime(2024, 1, 2, hour=5, tzinfo=timezone.utc)),
    ("1d 1H 1M", datetime(2024, 1, 2, hour=1, minute=1, tzinfo=timezone.utc)),
    ("1d 5M 2d", datetime(2024, 1, 3, minute=5, tzinfo=timezone.utc)),
])
def test_to_datetime_delta(delta, new_time):
    print(filters.to_datetime(delta))
    returned = datetime(2024, 1, 1, tzinfo=timezone.utc) + filters.to_datetime(delta)
    assert returned == new_time, "Generated datetime should convert to datetime"
