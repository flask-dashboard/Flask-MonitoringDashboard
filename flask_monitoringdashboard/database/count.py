from sqlalchemy import func, distinct

from flask_monitoringdashboard.database import session_scope, FunctionCall, Outlier


def count_rows(column, *criterion):
    """
    Count the number of rows of a specified column
    :param column: column to count
    :param criterion: where-clause of the query
    :return: number of rows
    """
    with session_scope() as db_session:
        result = db_session.query(func.count(distinct(column))).filter(*criterion).first()
        if result:
            return result[0]
        return 0


def count_users(endpoint):
    """
    :param endpoint: filter on this endpoint
    :return: The number of distinct users that have requested this endpoint
    """
    return count_rows(FunctionCall.group_by, FunctionCall.endpoint == endpoint)


def count_ip(endpoint):
    """
    :param endpoint: filter on this endpoint
    :return: The number of distinct users that have requested this endpoint
    """
    return count_rows(FunctionCall.ip, FunctionCall.endpoint == endpoint)


def count_versions(endpoint):
    """
    :param endpoint: filter on this endpoint
    :return: The number of distinct versions that are used for this endpoint
    """
    return count_rows(FunctionCall.version, FunctionCall.endpoint == endpoint)


def count_requests(endpoint, *where):
    """ Return the number of hits for a specific endpoint (possible with more filter arguments).
    :param endpoint: name of the endpoint
    :param where: additional arguments
    """
    return count_rows(FunctionCall.id, FunctionCall.endpoint == endpoint, *where)


def count_outliers(endpoint):
    """
    :return: An integer with the number of rows in the Outlier-table.
    """
    return count_rows(Outlier.id, Outlier.endpoint == endpoint)
