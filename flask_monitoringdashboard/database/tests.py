"""
Contains all functions that returns results of all tests
"""
from sqlalchemy import func, desc

from flask_monitoringdashboard.database import TestRun, TestsGrouped, TestedEndpoints


def add_test_result(db_session, name, exec_time, time, version, suite, iteration):
    """ Add a test result to the database. """
    db_session.add(TestRun(name=name, execution_time=exec_time, time=time, version=version, suite=suite, run=iteration))


def get_test_cnt_avg(db_session):
    """ Return all entries of measurements with their average. The results are grouped by their name. """
    return db_session.query(TestRun.name,
                            func.count(TestRun.execution_time).label('count'),
                            func.avg(TestRun.execution_time).label('average')
                            ).group_by(TestRun.name).order_by(desc('count')).all()


def get_test_suites(db_session, limit=None):
    """ Returns all test suites that have been run. """
    query = db_session.query(TestRun.suite).group_by(TestRun.suite).order_by(desc(TestRun.suite))
    if limit:
        query = query.limit(limit)
    return query.all()


def get_travis_builds(db_session, limit=None):
    """ Returns all Travis builds that have been run. """
    query = db_session.query(TestedEndpoints.travis_job_id).group_by(TestedEndpoints.travis_job_id).order_by(
        desc(TestedEndpoints.travis_job_id))
    if limit:
        query = query.limit(limit)
    return sorted([int(build[0]) for build in query.all()], reverse=True)


def get_suite_measurements(db_session, suite):
    """ Return all measurements for some Travis build. Used for creating a box plot. """
    result = [result[0] for result in db_session.query(TestRun.execution_time).filter(TestRun.suite == suite).all()]
    return result if len(result) > 0 else [0]


def get_endpoint_measurements(db_session, suite):
    """ Return all measurements for some Travis build. Used for creating a box plot. """
    result = [result[0] for result in
              db_session.query(TestedEndpoints.execution_time).filter(TestedEndpoints.travis_job_id == suite).all()]
    return result if len(result) > 0 else [0]


def get_endpoint_measurements_job(db_session, name, job_id):
    """ Return all measurements for some test of some Travis build. Used for creating a box plot. """
    result = db_session.query(TestedEndpoints.execution_time).filter(
        TestedEndpoints.endpoint_name == name).filter(TestedEndpoints.travis_job_id == job_id).all()
    return [r[0] for r in result] if len(result) > 0 else [0]


def get_last_tested_times(db_session):
    """ Returns the last tested time of each of the endpoints. """
    return db_session.query(TestedEndpoints.endpoint_name, func.max(TestedEndpoints.time_added)).group_by(
        TestedEndpoints.endpoint_name).all()
