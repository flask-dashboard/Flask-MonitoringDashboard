"""
Contains all functions that access a single endpoint
"""
import datetime

from sqlalchemy import func, desc
from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import session_scope, FunctionCall, MonitorRule


def get_num_requests(endpoint, start_date, end_date):
    """ Returns a list with all dates on which an endpoint is accessed.
        :param endpoint: if None, the result is the sum of all endpoints
        :param start_date: datetime.date object
        :param end_date: datetime.date object
    """
    with session_scope() as db_session:
        query = db_session.query(func.strftime('%Y-%m-%d %H:00:00', FunctionCall.time).label('newTime'),
                                 func.count(FunctionCall.execution_time).label('count'))
        if endpoint:
            query = query.filter(FunctionCall.endpoint == endpoint)
        result = query.filter(FunctionCall.time >= datetime.datetime.combine(start_date, datetime.time(0, 0, 0, 0))). \
            filter(FunctionCall.time <= datetime.datetime.combine(end_date, datetime.time(23, 59, 59))). \
            group_by('newTime').all()
        db_session.expunge_all()
        return result


def get_group_by_sorted(endpoint, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to filter the most used
    distinct
    :param endpoint: the endpoint to filter on
    :param limit: the number of
    :return: a list with the group_by as strings.
    """
    with session_scope() as db_session:
        query = db_session.query(FunctionCall.group_by, func.count(FunctionCall.group_by)). \
            filter(FunctionCall.endpoint == endpoint).group_by(FunctionCall.group_by). \
            order_by(desc(func.count(FunctionCall.group_by)))
        if limit:
            query = query.limit(limit)
        result = query.all()
        db_session.expunge_all()
        return [r[0] for r in result]


def get_ip_sorted(endpoint, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to filter the most used
    distinct
    :param endpoint: the endpoint to filter on
    :param limit: the number of
    :return: a list with the group_by as strings.
    """
    with session_scope() as db_session:
        query = db_session.query(FunctionCall.ip, func.count(FunctionCall.ip)). \
            filter(FunctionCall.endpoint == endpoint).group_by(FunctionCall.ip). \
            order_by(desc(func.count(FunctionCall.ip)))
        if limit:
            query = query.limit(limit)
        result = query.all()
        db_session.expunge_all()
        return [r[0] for r in result]


def get_monitor_rule(endpoint):
    """ Get the MonitorRule from a given endpoint. If no value is found, a new value 
    is added to the database and the function is called again (recursively). """
    try:
        with session_scope() as db_session:
            result = db_session.query(MonitorRule). \
                filter(MonitorRule.endpoint == endpoint).one()
            # for using the result when the session is closed, use expunge
            db_session.expunge(result)
            return result
    except NoResultFound:
        with session_scope() as db_session:
            db_session.add(
                MonitorRule(endpoint=endpoint, version_added=config.version, time_added=datetime.datetime.now()))

        # return new added row
        return get_monitor_rule(endpoint)


def update_monitor_rule(endpoint, value):
    """ Update the value of a specific monitor rule. """
    with session_scope() as db_session:
        db_session.query(MonitorRule).filter(MonitorRule.endpoint == endpoint). \
            update({MonitorRule.monitor: value})


def get_all_measurement_per_column(endpoint, column, value):
    """Return all entries with measurements from a given endpoint for which the column has a specific value.
    Used for creating a box plot. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall).filter(FunctionCall.endpoint == endpoint, column == value).all()
        db_session.expunge_all()
        return result


def get_last_accessed_times(endpoint):
    """ Returns a list of all endpoints and their last accessed time. """
    with session_scope() as db_session:
        result = db_session.query(MonitorRule.last_accessed).filter(MonitorRule.endpoint == endpoint).first()
        db_session.expunge_all()
        if result:
            return result[0]
        return None


def update_last_accessed(endpoint, value):
    """ Updates the timestamp of last access of the endpoint. """
    with session_scope() as db_session:
        db_session.query(MonitorRule).filter(MonitorRule.endpoint == endpoint). \
            update({MonitorRule.last_accessed: value})
