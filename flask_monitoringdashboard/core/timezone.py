import pytz


def to_local_datetime(datetime):
    """ Convert datetime (UTC) to local datetime based on the configuration """
    from flask_monitoringdashboard import config

    if datetime:
        return datetime.replace(tzinfo=pytz.utc).astimezone(config.timezone)
    return None


def to_utc_datetime(datetime):
    """ Convert datetime (local) to UTC datetime based on the configuration """
    from flask_monitoringdashboard import config

    if datetime:
        return datetime.replace(tzinfo=config.timezone).astimezone(pytz.utc)
    return None
