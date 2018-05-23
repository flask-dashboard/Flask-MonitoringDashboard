"""
Contains all functions that returns results of all monitor_rules
"""
from flask_monitoringdashboard.database import MonitorRule


def get_monitor_rules(db_session):
    """ Return all monitor rules that are currently being monitored"""
    result = db_session.query(MonitorRule).filter(MonitorRule.monitor).all()
    db_session.expunge_all()
    return result


def get_monitor_data(db_session):
    """
    Returns all data in the rules-table. This table contains which endpoints are being
    monitored and which are not.
    :return: all data from the database in the rules-table.
    """
    result = db_session.query(MonitorRule.endpoint, MonitorRule.last_accessed, MonitorRule.monitor,
                              MonitorRule.time_added, MonitorRule.version_added).all()
    db_session.expunge_all()
    return result
