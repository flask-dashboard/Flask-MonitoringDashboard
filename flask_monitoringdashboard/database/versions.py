from sqlalchemy import func, distinct, desc

from flask_monitoringdashboard.database import Request


def get_versions(db_session, endpoint_id=None, limit=None):
    """
    Returns a list of length 'limit' with the versions that are used in the application
    :param db_session: session for the database
    :param endpoint_id: only get the version that are used in this endpoint
    :param limit: only return the most recent versions
    :return: a list with the versions (as a string)
    """
    query = db_session.query(Request.version_requested)
    if endpoint_id:
        query = query.filter(Request.endpoint_id == endpoint_id)
    query = query.group_by(Request.version_requested)
    query = query.order_by(func.min(Request.time_requested))
    if limit:
        query = query.limit(limit)
    return list(reversed([r[0] for r in query.all()]))


def get_first_requests(db_session, endpoint_id, limit=None):
    """
    Returns a list with all versions and when they're first used
    :param db_session: session for the database
    :param limit: only return the most recent versions
    :param endpoint_id: id of the endpoint
    :return list of tuples with versions
    """
    query = db_session.query(Request.version_requested, func.min(Request.time_requested).label('first_used')).\
        filter(Request.endpoint_id == endpoint_id).\
        group_by(Request.version_requested).order_by(desc('first_used'))
    if limit:
        query = query.limit(limit)
    return query.all()
