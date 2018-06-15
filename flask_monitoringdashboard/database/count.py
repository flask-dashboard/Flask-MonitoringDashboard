from sqlalchemy import func, distinct

from flask_monitoringdashboard.database import Request, StackLine, TestResult, TestEndpoint


def count_rows(db_session, column, *criterion):
    """
    Count the number of rows of a specified column.
    :param db_session: session for the database
    :param column: column to count
    :param criterion: where-clause of the query
    :return: number of rows
    """
    result = db_session.query(func.count(distinct(column))).filter(*criterion).first()
    if result:
        return result[0]
    return 0


def count_users(db_session, endpoint_id):
    """
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return: The number of distinct users that have requested this endpoint
    """
    return count_rows(db_session, Request.group_by, Request.endpoint_id == endpoint_id)


def count_ip(db_session, endpoint_id):
    """
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return: The number of distinct users that have requested this endpoint
    """
    return count_rows(db_session, Request.ip, Request.endpoint_id == endpoint_id)


def count_versions(db_session):
    """
    :param db_session: session for the database
    :return: The number of distinct versions that are used
    """
    return count_rows(db_session, Request.version_requested)


def count_test_builds(db_session):
    """
    :param db_session: session for the database
    :return: The number of Travis builds that are available
    """
    return count_rows(db_session, TestResult.travis_job_id)


def count_builds_endpoint(db_session):
    """
    :param db_session: session for the database
    :return: The number of Travis builds that are available
    """
    return count_rows(db_session, TestEndpoint.travis_job_id)


def count_versions_endpoint(db_session, endpoint_id):
    """
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return: The number of distinct versions that are used for this endpoint
    """
    return count_rows(db_session, Request.version_requested, Request.endpoint_id == endpoint_id)


def count_requests(db_session, endpoint_id, *where):
    """
    Return the number of hits for a specific endpoint (possible with more filter arguments).
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :param where: additional arguments
    """
    return count_rows(db_session, Request.id, Request.endpoint_id == endpoint_id, *where)


def count_total_requests(db_session, *where):
    """
    Return the number of total hits
    :param db_session: session for the database
    :param where: additional arguments
    """
    return count_rows(db_session, Request.id, *where)


def count_outliers(db_session, endpoint_id):
    """
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return: An integer with the number of rows in the Outlier-table.
    """
    return count_rows(db_session, Request.id, Request.endpoint_id == endpoint_id, Request.outlier)


def count_profiled_requests(db_session, endpoint_id):
    """
    Count the number of profiled requests for a certain endpoint
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return: An integer
    """
    count = db_session.query(func.count(distinct(StackLine.request_id))). \
        filter(Request.endpoint_id == endpoint_id).\
        join(Request.stack_lines).first()
    if count:
        return count[0]
    return 0
