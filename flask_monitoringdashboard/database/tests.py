"""
Contains all functions that returns results of all tests
"""
from sqlalchemy import func, desc

from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database import TestRun


def add_test_result(db_session, name, exec_time, time, version, suite, iteration):
    """ Add a test result to the database. """
    db_session.add(TestRun(name=name, execution_time=exec_time, time=time, version=version, suite=suite, run=iteration))


def get_next_suite_nr(db_session):
    """ Retrieves the number of the next suite to run. """
    result = db_session.query(func.max(TestRun.suite).label('nr')).one()
    if result.nr:
        return result.nr + 1
    return 1


def get_test_cnt_avg(db_session):
    """ Return all entries of measurements with their average. The results are grouped by their name. """
    return db_session.query(TestRun.name,
                            func.count(TestRun.execution_time).label('count'),
                            func.avg(TestRun.execution_time).label('average')
                            ).group_by(TestRun.name).order_by(desc('count')).all()


def get_test_suites(db_session):
    """ Returns all test suites that have been run. """
    return db_session.query(TestRun.suite).group_by(TestRun.suite).all()


def get_suite_measurements(db_session, suite):
    """ Return all measurements for some Travis build. Used for creating a box plot. """
    return db_session.query(TestRun).filter(TestRun.suite == suite).all()


def get_test_measurements(db_session, name, suite):
    """ Return all measurements for some test of some Travis build. Used for creating a box plot. """
    return db_session.query(TestRun).filter(TestRun.name == name, TestRun.suite == suite).all()


def get_last_tested_times(db_session, test_groups):
    """ Returns the last tested time of each of the endpoints. """
    res = {}
    for group in test_groups:
        if group.endpoint not in res:
            res[group.endpoint] = db_session.query(TestRun.time).filter(TestRun.name == group.test_name).all()[0].time
    result = []
    for endpoint in res:
        result.append((endpoint, to_local_datetime(res[endpoint])))
    return result
