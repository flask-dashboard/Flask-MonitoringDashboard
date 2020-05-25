import datetime

from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime


def test_timezone():
    dt = datetime.datetime.now()
    assert to_local_datetime(to_utc_datetime(dt)) == dt
    assert to_utc_datetime(to_local_datetime(dt)) == dt


def test_timezone_none():
    assert to_local_datetime(None) is None
    assert to_utc_datetime(None) is None
