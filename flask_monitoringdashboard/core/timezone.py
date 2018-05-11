import pytz


def to_local_datetime(datetime):
    """ Convert datetime (UTC) to local datetime from the configuration """
    from flask_monitoringdashboard import config

    if datetime:
        return datetime.replace(tzinfo=pytz.utc).astimezone(config.timezone)
    return None
