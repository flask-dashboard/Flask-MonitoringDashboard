from sqlalchemy import distinct, asc

from flask_monitoringdashboard.database import session_scope, FunctionCall


def get_date_first_request(version=None):
    """
    :param version: optional: first date when this version is requested
    :return: a datetime object with the value of when the first request is made
    """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.time).\
            filter((FunctionCall.version == version) | (version is None)).first()
        if result:
            return result[0]
        return None


def get_versions(end=None):
    """
    Returns a list of length 'limit' with the versions that are used in the application
    :param end: the versions that are used in a specific endpoint
    :param limit: the maximum length of the returned list
    :return: a list with the versions (as a string)
    """
    with session_scope() as db_session:
        result = db_session.query(distinct(FunctionCall.version)). \
            filter((FunctionCall.endpoint == end) | (end is None)). \
            order_by(asc(FunctionCall.time)).all()
        db_session.expunge_all()
    return [row[0] for row in result]
