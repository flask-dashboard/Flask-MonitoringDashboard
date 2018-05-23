"""
Contains all functions that access a single endpoint
"""
import datetime

from sqlalchemy import func, desc
from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database import FunctionCall, MonitorRule


def get_num_requests(db_session, endpoint, start_date, end_date):
    """ Returns a list with all dates on which an endpoint is accessed.
        :param db_session: session containing the query
        :param endpoint: if None, the result is the sum of all endpoints
        :param start_date: datetime.date object
        :param end_date: datetime.date object
    """
    query = db_session.query(FunctionCall.time)
    if endpoint:
        query = query.filter(FunctionCall.endpoint == endpoint)
    result = query.filter(FunctionCall.time >= start_date, FunctionCall.time <= end_date).all()

    return group_execution_times(result)


def group_execution_times(times):
    """
    Returns a list of tuples containing the number of hits per hour
    :param times: list of datetime objects
    :return: list of tuples ('%Y-%m-%d %H:00:00', count)
    """
    hours_dict = {}
    for dt in times:
        round_time = dt.time.strftime('%Y-%m-%d %H:00:00')
        hours_dict[round_time] = hours_dict.get(round_time, 0) + 1
    return hours_dict.items()


def get_users(db_session, endpoint, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to filter the most used
    distinct.
    :param db_session: session containing the query
    :param endpoint: the endpoint to filter on
    :param limit: the number of
    :return: a list with the group_by as strings.
    """
    query = db_session.query(FunctionCall.group_by, func.count(FunctionCall.group_by)). \
        filter(FunctionCall.endpoint == endpoint).group_by(FunctionCall.group_by). \
        order_by(desc(func.count(FunctionCall.group_by)))
    if limit:
        query = query.limit(limit)
    result = query.all()
    db_session.expunge_all()
    return [r[0] for r in result]


def get_ips(db_session, endpoint, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to filter the most used
    distinct.
    :param db_session: session containing the query
    :param endpoint: the endpoint to filter on
    :param limit: the number of
    :return: a list with the group_by as strings.
    """
    query = db_session.query(FunctionCall.ip, func.count(FunctionCall.ip)). \
        filter(FunctionCall.endpoint == endpoint).group_by(FunctionCall.ip). \
        order_by(desc(func.count(FunctionCall.ip)))
    if limit:
        query = query.limit(limit)
    result = query.all()
    db_session.expunge_all()
    return [r[0] for r in result]


def get_monitor_rule(db_session, endpoint):
    """ Get the MonitorRule from a given endpoint. If no value is found, a new value 
    is added to the database and the function is called again (recursively). """
    try:
        result = db_session.query(MonitorRule). \
            filter(MonitorRule.endpoint == endpoint).one()
        result.time_added = to_local_datetime(result.time_added)
        result.last_accessed = to_local_datetime(result.last_accessed)
        db_session.expunge_all()
        return result
    except NoResultFound:
        db_session.add(
            MonitorRule(endpoint=endpoint, version_added=config.version, time_added=datetime.datetime.utcnow()))

    # return new added row
    return get_monitor_rule(db_session, endpoint)


def update_monitor_rule(db_session, endpoint, value):
    """ Update the value of a specific monitor rule. """
    db_session.query(MonitorRule).filter(MonitorRule.endpoint == endpoint). \
        update({MonitorRule.monitor: value})


def get_last_accessed_times(db_session):
    """ Returns the accessed time of a single endpoint. """
    result = db_session.query(MonitorRule.endpoint, MonitorRule.last_accessed).all()
    return [(end, to_local_datetime(time)) for end, time in result]


def update_last_accessed(db_session, endpoint, value):
    """ Updates the timestamp of last access of the endpoint. """
    db_session.query(MonitorRule).filter(MonitorRule.endpoint == endpoint). \
        update({MonitorRule.last_accessed: value})
