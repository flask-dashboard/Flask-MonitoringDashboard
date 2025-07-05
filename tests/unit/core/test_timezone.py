import datetime

from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime


def test_timezone():
    dt = datetime.datetime.now(datetime.timezone.utc)
    # Convert to local and back to UTC should give the same result
    local_dt = to_local_datetime(dt)
    assert to_utc_datetime(local_dt) == dt
    # Convert to UTC and back to local should give the same result
    utc_dt = to_utc_datetime(local_dt)
    assert to_local_datetime(utc_dt) == local_dt


def test_timezone_none():
    assert to_local_datetime(None) is None
    assert to_utc_datetime(None) is None
