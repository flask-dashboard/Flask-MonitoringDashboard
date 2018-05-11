import datetime


def to_local_datetime(dt):
    """ Convert datetime (UTC) to local datetime based on the configuration """
    from flask_monitoringdashboard import config

    if dt:
        return dt + config.timezone.utcoffset(datetime.datetime.utcnow())
    return None


def to_utc_datetime(dt):
    """ Convert datetime (local) to UTC datetime based on the configuration """
    from flask_monitoringdashboard import config

    if dt:
        return dt - config.timezone.utcoffset(datetime.datetime.utcnow())
    return None
