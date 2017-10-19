"""
Contains all functions that returns results of all monitor_rules
"""
from dashboard.database import session_scope, MonitorRule


def get_monitor_rules():
    """ Return all monitor rules that are currently being monitored"""
    with session_scope() as db_session:
        result = db_session.query(MonitorRule).filter(MonitorRule.monitor).all()
        db_session.expunge_all()
        return result


def get_monitor_names():
    """ Return all names of monitor rules that are currently being monitored"""
    with session_scope() as db_session:
        result = db_session.query(MonitorRule.endpoint).filter(MonitorRule.monitor).all()
        db_session.expunge_all()
        return result


def reset_monitor_endpoints():
    """ Update all monitor rules in the database and set them to false. """
    with session_scope() as db_session:
        db_session.query(MonitorRule).update({MonitorRule.monitor: False})
