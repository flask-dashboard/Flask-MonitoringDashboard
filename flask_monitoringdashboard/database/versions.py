from sqlalchemy import distinct, asc

from flask_monitoringdashboard.database import FunctionCall


def get_date_first_request(db_session, version=None):
    """
    :param version: optional: first date when this version is requested
    :return: a datetime object with the value of when the first request is made
    """
    result = db_session.query(FunctionCall.time). \
        filter((FunctionCall.version == version) | (version is None)).first()
    if result:
        return result[0]
    return None


def get_versions(db_session, end=None):
    """
    Returns a list of length 'limit' with the versions that are used in the application
    :param end: the versions that are used in a specific endpoint
    :return: a list with the versions (as a string)
    """
    result = db_session.query(distinct(FunctionCall.version)). \
        filter((FunctionCall.endpoint == end) | (end is None)). \
        order_by(asc(FunctionCall.time)).all()
    return [row[0] for row in result]
