"""
Contains all functions that access any functionCall-object
"""

import datetime
import time

from sqlalchemy import func, distinct

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import session_scope, FunctionCall
from flask_monitoringdashboard.database.count import count_requests


def get_requests_per_day(endpoint, list_of_days):
    """
    :param endpoint: name of the endpoint
    :param list_of_days: a list with datetime.date objects
    :return: A list of the amount of requests per day for a specific endpoint.
    If no requests is made on that day, a value of 0 is returned.
    """
    result_list = []
    with session_scope() as db_session:
        for day in list_of_days:
            result = db_session.query(FunctionCall.execution_time). \
                filter(FunctionCall.endpoint == endpoint). \
                filter(func.strftime('%Y-%m-%d', FunctionCall.time) == day.strftime('%Y-%m-%d')).count()
            result_list.append(result)
    return result_list


def add_function_call(execution_time, endpoint, ip):
    """ Add a measurement to the database. """
    with session_scope() as db_session:
        db_session.add(FunctionCall(endpoint=endpoint, execution_time=execution_time, version=config.version, ip=ip))


def get_median(endpoint, *where):
    """ Return the median for a specific endpoint within a certain time interval.
    If date_from is not specified, all results are counted
    :param endpoint: name of the endpoint
    :param where: additional where clause
    """
    num_rows = count_requests(endpoint, *where)
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.execution_time). \
            filter(FunctionCall.endpoint == endpoint, *where). \
            order_by(FunctionCall.execution_time).limit(2 - num_rows % 2).offset((num_rows - 1) / 2).all()
        values = [r[0] for r in result]
        return sum(values) / max(1, len(values))


def get_data_between(time_from, time_to=None):
    """
        Returns all data in the FunctionCall table, for the export data option.
        This function returns all data after the time_from date.
    """
    with session_scope() as db_session:
        query = db_session.query(FunctionCall).filter(FunctionCall.time > time_from)
        if time_to:
            query = query.filter(FunctionCall.time <= time_to)
        result = query.all()
        db_session.expunge_all()
        return result


def get_data():
    """
    Equivalent function to get_data_from, but returns all data.
    :return: all data from the database in the Endpoint-table.
    """
    return get_data_between(datetime.date(1970, 1, 1), datetime.datetime.utcnow())


def get_data_per_version(version):
    """ Returns all data in the FunctionCall table, grouped by their version. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.execution_time, FunctionCall.version). \
            filter(FunctionCall.version == version).all()
        db_session.expunge_all()
        return result


def get_data_per_endpoint(end):
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.execution_time, FunctionCall.endpoint). \
            filter(FunctionCall.endpoint == end).all()
        db_session.expunge_all()
        return result


def get_endpoints():
    """ Returns the name of all endpoints from the database """
    with session_scope() as db_session:
        result = db_session.query(distinct(FunctionCall.endpoint)).order_by(FunctionCall.endpoint).all()
        db_session.expunge_all()
        return [r[0] for r in result]  # unpack tuple result


def get_date_of_first_request():
    """ return the date (as unix timestamp) of the first request """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.time).first()
        if result:
            return int(time.mktime(result[0].timetuple()))
        return -1
