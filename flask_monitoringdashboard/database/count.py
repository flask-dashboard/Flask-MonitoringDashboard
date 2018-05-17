from sqlalchemy import func, distinct

from flask_monitoringdashboard.database import FunctionCall, Outlier, TestRun


def count_rows(db_session, column, *criterion):
    """
    Count the number of rows of a specified column
    :param column: column to count
    :param criterion: where-clause of the query
    :return: number of rows
    """
    result = db_session.query(func.count(distinct(column))).filter(*criterion).first()
    if result:
        return result[0]
    return 0


def count_users(db_session, endpoint):
    """
    :param endpoint: filter on this endpoint
    :return: The number of distinct users that have requested this endpoint
    """
    return count_rows(db_session, FunctionCall.group_by, FunctionCall.endpoint == endpoint)


def count_ip(db_session, endpoint):
    """
    :param endpoint: filter on this endpoint
    :return: The number of distinct users that have requested this endpoint
    """
    return count_rows(db_session, FunctionCall.ip, FunctionCall.endpoint == endpoint)


def count_versions(db_session):
    """
    :return: The number of distinct versions that are used
    """
    return count_rows(db_session, FunctionCall.version)


def count_builds(db_session):
    """
    :return: The number of Travis builds that are available
    """
    return count_rows(db_session, TestRun.suite)


def count_versions_end(db_session, endpoint):
    """
    :param endpoint: filter on this endpoint
    :return: The number of distinct versions that are used for this endpoint
    """
    return count_rows(db_session, FunctionCall.version, FunctionCall.endpoint == endpoint)


def count_requests(db_session, endpoint, *where):
    """ Return the number of hits for a specific endpoint (possible with more filter arguments).
    :param endpoint: name of the endpoint
    :param where: additional arguments
    """
    return count_rows(db_session, FunctionCall.id, FunctionCall.endpoint == endpoint, *where)


def count_total_requests(db_session, *where):
    """ Return the number of total hits
    :param db_session: session for the database
    :param where: additional arguments
    """
    return count_rows(db_session, FunctionCall.id, *where)


def count_outliers(db_session, endpoint):
    """
    :return: An integer with the number of rows in the Outlier-table.
    """
    return count_rows(db_session, Outlier.id, Outlier.endpoint == endpoint)
