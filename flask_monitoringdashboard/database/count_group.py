from sqlalchemy import func

from flask_monitoringdashboard.database import FunctionCall


def count_rows_group(db_session, column, *criterion):
    """
    Count the number of rows of a specified column
    :param db_session: session for the database
    :param column: column to count
    :param criterion: where-clause of the query
    :return: list with the number of rows per endpoint
    """
    return db_session.query(FunctionCall.endpoint, func.count(column)).\
        filter(*criterion).group_by(FunctionCall.endpoint).all()


def get_value(list, name, default=0):
    """
    :param list: must be structured as: [(a, b), (c, d), ..]
    :param name: name to filter on, e.g.: if name == a, it returns b
    :param default: returned if the name was not found in the list
    :return: value corresponding to the name in the list.
    """
    for key, value in list:
        if key == name:
            return value
    return default


def count_requests_group(db_session, *where):
    """ Return the number of hits for all endpoints (possible with more filter arguments).
    :param db_session: session for the database
    :param where: additional arguments
    """
    return count_rows_group(db_session, FunctionCall.id, *where)


def count_requests_per_day(db_session, list_of_days):
    """ Return the number of hits for all endpoints per day.
    :param db_session: session for the database
    :param list_of_days: list with datetime.datetime objects. """
    return [count_rows_group(db_session, FunctionCall.id, func.date(FunctionCall.time) == day)
            for day in list_of_days]
