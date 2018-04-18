"""
Contains all functions that access any functionCall-object
"""

import datetime
import time

from sqlalchemy import func, desc, text, asc

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import session_scope, FunctionCall

PRIMITIVES = (bool, bytes, float, int, str)


def get_reqs_endpoint_day():
    """ Retrieves the number of requests per endpoint per day. """
    with session_scope() as db_session:
        query = text("""SELECT strftime('%Y-%m-%d', time) AS newTime,
                               count(endpoint) AS cnt,
                               endpoint
                        FROM functioncalls 
                        GROUP BY newTime, endpoint""")
        result = db_session.execute(query)
        data = result.fetchall()
        return data


def get_group_by(argument):
    """ Returns the result of the given argument. The result is computed as:
    - If the argument is a primitive (i.e. str, bool, int, ...) return its value.
    - If the argument is a function, call the function.
    - If the argument is iterable (i.e. list or tuple), compute the result by iterating over the argument
    Return type is always a string"""

    if type(argument) in PRIMITIVES:
        return str(argument)

    if callable(argument):
        return get_group_by(argument())

    # Try if the argument is iterable (i.e. tuple or list)
    try:
        result_list = [get_group_by(i) for i in argument]
        result_string = ','.join(result_list)
        return '({})'.format(result_string)
    except TypeError:
        # Cannot deal with this
        return str(argument)


def add_function_call(time, endpoint, ip):
    """ Add a measurement to the database. """
    with session_scope() as db_session:
        group_by = None
        try:
            if config.group_by:
                group_by = get_group_by(config.group_by)
                print(group_by)
        except Exception as e:
            print('Can\'t execute group_by function: {}'.format(e))
        call = FunctionCall(endpoint=endpoint, execution_time=time, version=config.version,
                            time=datetime.datetime.now(), group_by=str(group_by), ip=ip)
        db_session.add(call)


def get_times():
    """ Return all entries of measurements with the average and total number of execution times. The results are 
    grouped by their endpoint. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.endpoint,
                                  func.count(FunctionCall.execution_time).label('count'),
                                  func.avg(FunctionCall.execution_time).label('average')
                                  ).group_by(FunctionCall.endpoint).order_by(desc('count')).all()
        db_session.expunge_all()
        return result


def get_hits(endpoint, date_from=datetime.datetime.utcfromtimestamp(0)):
    """ Return the number of hits for a specific endpoint within a certain time interval.
    If date_from is not specified, all results are counted
    :param endpoint: name of the endpoint
    :param date_from: A datetime-object
    """
    with session_scope() as db_session:
        result = db_session.query(func.count(FunctionCall.execution_time).label('count')). \
            filter(FunctionCall.endpoint == endpoint).filter(FunctionCall.time > date_from). \
            group_by(FunctionCall.endpoint).first()
        db_session.expunge_all()
        if result:
            return result[0]
        return 0


def get_median(endpoint, date_from=datetime.datetime.utcfromtimestamp(0)):
    """ Return the median for a specific endpoint within a certain time interval.
    If date_from is not specified, all results are counted
    :param endpoint: name of the endpoint
    :param date_from: A datetime-object
    """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.execution_time). \
            filter(FunctionCall.endpoint == endpoint).filter(FunctionCall.time > date_from). \
            order_by(FunctionCall.execution_time).all()
        result_list = [r[0] for r in result]
        return median_value(result_list)


def median_value(result_list):
    """ Takes the median value from a list.
    Note that the given result_list must be sorted"""
    count = len(result_list)
    if count == 0:
        return 0
    if count % 2 == 1:
        return result_list[count // 2]
    else:
        return (result_list[count // 2 - 1] + result_list[count // 2]) / 2


def get_data_between(time_from, time_to=None):
    """
        Returns all data in the FunctionCall table, for the export data option.
        This function returns all data after the time_from date.
    """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall).filter(FunctionCall.time >= time_from)
        if time_to:
            result = result.filter(FunctionCall.time < time_to)
        result = result.all()
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


def get_hits_per_version(version):
    """ Returns the hits per endpoint per version """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.endpoint,
                                  FunctionCall.version,
                                  func.count(FunctionCall.endpoint).label('count')). \
            filter(FunctionCall.version == version). \
            group_by(FunctionCall.endpoint).all()
        db_session.expunge_all()
        return result


def get_versions(end=None):
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.version,
                                  func.min(FunctionCall.time).label('startedUsingOn')). \
            filter((FunctionCall.endpoint == end) | (end is None)). \
            group_by(FunctionCall.version). \
            order_by(asc('startedUsingOn')).all()
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
        result = db_session.query(FunctionCall.endpoint).distinct().all()
        db_session.expunge_all()
        return [r[0] for r in result]  # unpack tuple result


def get_endpoints_with_count():
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.endpoint,
                                  func.count(FunctionCall.endpoint).label('cnt')). \
            group_by(FunctionCall.endpoint).order_by(asc('cnt')).all()
        db_session.expunge_all()
        return result


def get_date_of_first_request():
    """ return the date (as unix timestamp) of the first request """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.time).first()
        if result:
            return int(time.mktime(result[0].timetuple()))
        return -1
