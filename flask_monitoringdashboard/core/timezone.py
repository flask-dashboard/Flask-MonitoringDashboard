import datetime


def to_local_datetime(dt):
    """
    Convert datetime (UTC) to local datetime based on the configuration.
    :param dt: UTC datetime object
    :return local datetime
    """
    from flask_monitoringdashboard import config

    if dt:
        return dt + config.timezone.utcoffset(datetime.datetime.utcnow())
    return None


def to_utc_datetime(dt):
    """
    Convert datetime (local) to UTC datetime based on the configuration.
    :param dt: local datetime object
    :return UTC datetime
    """
    from flask_monitoringdashboard import config

    if dt:
        return dt - config.timezone.utcoffset(datetime.datetime.utcnow())
    return None
