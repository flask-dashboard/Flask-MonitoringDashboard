"""
Contains all functions that returns results of all tests
"""
from sqlalchemy import func, desc

from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database import TestRun, TestsGrouped


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


def get_suite_measurements(db_session, suite):
    """ Return all measurements for some Travis build. Used for creating a box plot. """
    result = [result[0] for result in db_session.query(TestRun.execution_time).filter(TestRun.suite == suite).all()]
    return result if len(result) > 0 else [0]


def get_test_measurements(db_session, name, suite):
    """ Return all measurements for some test of some Travis build. Used for creating a box plot. """
    result = []
    test_names = db_session.query(TestsGrouped.test_name).filter(TestsGrouped.endpoint == name).all()
    for test in test_names:
        result += [result[0] for result in
                   db_session.query(TestRun.execution_time).filter(TestRun.name == test[0],
                                                                   TestRun.suite == suite).all()]
    return result if len(result) > 0 else [0]


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
