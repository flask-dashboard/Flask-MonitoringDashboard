from sqlalchemy import func, asc, distinct, desc

from flask_monitoringdashboard.database import FunctionCall


def get_versions(db_session, end=None, limit=None):
    """
    Returns a list of length 'limit' with the versions that are used in the application
    :param db_session: session for the database
    :param end: the versions that are used in a specific endpoint
    :param limit: only return the most recent versions
    :return: a list with the versions (as a string)
    """
    query = db_session.query(distinct(FunctionCall.version))
    if end:
        query = query.filter(FunctionCall.endpoint == end)
    query = query.order_by(desc(FunctionCall.version))
    if limit:
        query = query.limit(limit)
    return list(reversed([r[0] for r in query.all()]))


def get_first_requests(db_session):
    """
    Returns a list with all versions and when they're first used
    :param db_session: session for the database
    :return:
    """
    return db_session.query(FunctionCall.version, func.min(FunctionCall.time)).\
        group_by(FunctionCall.version).all()
