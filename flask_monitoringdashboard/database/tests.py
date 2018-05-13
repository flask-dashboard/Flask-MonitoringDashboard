"""
Contains all functions that returns results of all tests
"""
from sqlalchemy import func, desc

from flask_monitoringdashboard.database import TestRun


def get_test_names(db_session):
    """ Return all existing test names. """
    result = db_session.query(TestRun.name).distinct()
    db_session.expunge_all()
    return result


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


def get_test_cnt_avg_current(db_session, version):
    """ Return entries of measurements with their average from the current project version only. """
    return db_session.query(TestRun.name,
                            func.count(TestRun.execution_time).label('count'),
                            func.avg(TestRun.execution_time).label('average')) \
        .filter(TestRun.version == version) \
        .group_by(TestRun.name).order_by(desc('count')).all()


def get_test_suites(db_session):
    """ Returns all test suites that have been run. """
    return db_session.query(TestRun.suite).group_by(TestRun.suite).all()


def get_suite_measurements(db_session, suite):
    """ Return all measurements for some Travis build. Used for creating a box plot. """
    return db_session.query(TestRun).filter(TestRun.suite == suite).all()


def get_test_measurements(db_session, name, suite):
    """ Return all measurements for some test of some Travis build. Used for creating a box plot. """
    return db_session.query(TestRun).filter(TestRun.name == name, TestRun.suite == suite).all()
