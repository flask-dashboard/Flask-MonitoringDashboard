import datetime

from sqlalchemy import func

from flask_monitoringdashboard.core.timezone import to_utc_datetime
from flask_monitoringdashboard.database import Request, TestEndpoint, Endpoint


def get_latest_test_version(db_session):
    """
    Retrieves the latest version of the user app that was tested.
    :param db_session: session for the database
    :return latest test version
    """
    latest_time = db_session.query(func.max(TestEndpoint.time_added)).one()[0]
    if latest_time:
        return db_session.query(TestEndpoint.app_version).filter(TestEndpoint.time_added == latest_time).one()[0]
    return None


def count_rows_group(db_session, column, *criterion):
    """
    Count the number of rows of a specified column
    :param db_session: session for the database
    :param column: column to count
    :param criterion: where-clause of the query
    :return list with the number of rows per endpoint
    """
    return db_session.query(Request.endpoint_id, func.count(column)). \
        filter(*criterion).group_by(Request.endpoint_id).all()


def get_value(list, name, default=0):
    """
    :param list: must be structured as: [(a, b), (c, d), ..]
    :param name: name to filter on, e.g.: if name == a, it returns b
    :param default: returned if the name was not found in the list
    :return value corresponding to the name in the list.
    """
    for key, value in list:
        if key == name:
            return value
    return default


def count_requests_group(db_session, *where):
    """
    Return the number of hits for all endpoints (possible with more filter arguments).
    :param db_session: session for the database
    :param where: additional arguments
    """
    return count_rows_group(db_session, Request.id, *where)


def count_times_tested(db_session, *where):
    """ Return the number of tests for an endpoint (possibly with more filter arguments).
    :param db_session: session for the database
    :param where: additional arguments
    """
    result = db_session.query(Endpoint.name, func.count(TestEndpoint.endpoint_id)).join(
        TestEndpoint.endpoint).filter(*where).group_by(Endpoint.name).all()
    return result


def count_requests_per_day(db_session, list_of_days):
    """ Return the number of hits for all endpoints per day.
    :param db_session: session for the database
    :param list_of_days: list with datetime.datetime objects. """
    result = []
    for day in list_of_days:
        dt_begin = to_utc_datetime(datetime.datetime.combine(day, datetime.time(0, 0, 0)))
        dt_end = dt_begin + datetime.timedelta(days=1)

        result.append(count_rows_group(db_session, Request.id, Request.time_requested >= dt_begin,
                                       Request.time_requested < dt_end))
    return result
