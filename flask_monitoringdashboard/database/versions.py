from sqlalchemy import func, distinct, desc

from flask_monitoringdashboard.database import Request


def get_versions(db_session, end=None, limit=None):
    """
    Returns a list of length 'limit' with the versions that are used in the application
    :param db_session: session for the database
    :param end: the versions that are used in a specific endpoint
    :param limit: only return the most recent versions
    :return: a list with the versions (as a string)
    """
    query = db_session.query(distinct(Request.version))
    if end:
        query = query.filter(Request.endpoint == end)
    query = query.order_by(desc(Request.time))
    if limit:
        query = query.limit(limit)
    return list(reversed([r[0] for r in query.all()]))


def get_first_requests(db_session, limit=None):
    """
    Returns a list with all versions and when they're first used
    :param db_session: session for the database
    :param limit: only return the most recent versions
    :return:
    """
    query = db_session.query(Request.version, func.min(Request.time).label('first_used')). \
        group_by(Request.version).order_by(desc('first_used'))
    if limit:
        query = query.limit(limit)
    return query.all()
