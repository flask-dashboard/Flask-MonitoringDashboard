import datetime
from flask_monitoringdashboard.core.timezone import to_utc_datetime
from flask_monitoringdashboard.database import CountQueries


def get_value(tuples, name, default=0):
    """
    :param tuples: must be structured as: [(a, b), (c, d), ..]
    :param name: name to filter on, e.g.: if name == a, it returns b
    :param default: returned if the name was not found in the list
    :return value corresponding to the name in the list.
    """
    if tuples:
        for key, value in tuples:
            if key == name:
                return value
    return default


def count_requests_group(session, *where):
    """
    Return the number of hits for all endpoints (possible with more filter arguments).
    :param session: session for the database
    :param where: additional arguments
    """
    return CountQueries(session).count_request_per_endpoint(*where)


def count_requests_per_day(session, list_of_days):
    """ Return the number of hits for all endpoints per day.
    :param session: session for the database
    :param list_of_days: list with datetime.datetime objects. """
    result = []
    count_queries_obj = CountQueries(session)
    for day in list_of_days:
        dt_begin = to_utc_datetime(datetime.datetime.combine(day, datetime.time(0, 0, 0)))
        dt_end = dt_begin + datetime.timedelta(days=1)
        result.append(
            count_queries_obj.count_request_per_endpoint(*count_queries_obj.generate_time_query(dt_begin, dt_end)))
    return result
