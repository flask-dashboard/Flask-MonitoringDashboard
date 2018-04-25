import datetime

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


def count_requests(endpoint, date_from=datetime.datetime.utcfromtimestamp(0)):
    """ Return the number of hits for a specific endpoint within a certain time interval.
    If date_from is not specified, all results are counted
    :param endpoint: name of the endpoint
    :param date_from: A datetime-object
    """
    return count_rows(FunctionCall.id, FunctionCall.endpoint == endpoint, FunctionCall.time > date_from)


def count_hits(version, endpoint):
    """
    Same as count_requests, but now filter on version and endpoint
    :return: the number of hits for a specific endpoint in a specific version
    """
    return count_rows(FunctionCall.id, FunctionCall.endpoint == endpoint, FunctionCall.version == version)


def count_outliers(endpoint):
    """
    :return: An integer with the number of rows in the Outlier-table.
    """
    return count_rows(Outlier.id, Outlier.endpoint == endpoint)
