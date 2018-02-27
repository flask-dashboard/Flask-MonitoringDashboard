"""
Contains all functions that returns results of all tests
"""
from flask_monitoringdashboard.database import session_scope, Tests, TestRun
from sqlalchemy import func, desc


def get_tests():
    """ Return all existing tests. """
    with session_scope() as db_session:
        result = db_session.query(Tests).all()
        db_session.expunge_all()
        return result


def add_test(name):
    """ Add a newly found test to the database. """
    with session_scope() as db_session:
        db_session.add(Tests(name=name))


def add_or_update_test(name, last_run, succeeded):
    """ Updates values of a test. """
    with session_scope() as db_session:
        if db_session.query(Tests).filter(Tests.name == name).count():
            db_session.query(Tests).filter(Tests.name == name). \
                update({Tests.lastRun: last_run, Tests.succeeded: succeeded})
        else:
            db_session.add(Tests(name=name, lastRun=last_run, succeeded=succeeded))


def add_test_result(name, exec_time, time, version, suite, iter):
    """ Add a test result to the database. """
    with session_scope() as db_session:
        db_session.add(
            TestRun(name=name, execution_time=exec_time, time=time, version=version, suite=suite, run=iter))


def get_suite_nr():
    """ Retrieves the number of the next suite to run. """
    with session_scope() as db_session:
        result = db_session.query(func.max(TestRun.suite).label('nr')).one()
        if result.nr is None:
            next_nr = 1
        else:
            next_nr = result.nr + 1
        return next_nr


def get_results():
    """ Return all entries of measurements with their average. The results are grouped by their name. """
    with session_scope() as db_session:
        result = db_session.query(TestRun.name,
                                  func.count(TestRun.execution_time).label('count'),
                                  func.avg(TestRun.execution_time).label('average')
                                  ).group_by(TestRun.name).order_by(desc('count')).all()
        db_session.expunge_all()
        return result


def get_res_current(version):
    """ Return entries of measurements with their average from the current project version only. """
    with session_scope() as db_session:
        result = db_session.query(TestRun.name,
                                  func.count(TestRun.execution_time).label('count'),
                                  func.avg(TestRun.execution_time).label('average')) \
            .filter(TestRun.version == version) \
            .group_by(TestRun.name).order_by(desc('count')).all()
        db_session.expunge_all()
        return result


def get_line_results():
    with session_scope() as db_session:
        result = db_session.query(TestRun.version,
                                  func.avg(TestRun.execution_time).label('avg'),
                                  func.min(TestRun.execution_time).label('min'),
                                  func.max(TestRun.execution_time).label('max'),
                                  func.count(TestRun.execution_time).label('count')
                                  ).group_by(TestRun.version).order_by(desc('count')).all()
        db_session.expunge_all()
        return result


def get_suites():
    with session_scope() as db_session:
        result = db_session.query(TestRun.suite).group_by(TestRun.suite).all()
        db_session.expunge_all()
        return result


def get_measurements(suite):
    """Return all measurements for some Travis build. Used for creating a box plot. """
    with session_scope() as db_session:
        result = db_session.query(TestRun).filter(TestRun.suite == suite).all()
        db_session.expunge_all()
        return result


def get_test_measurements(name, suite):
    """Return all measurements for some test of some Travis build. Used for creating a box plot. """
    with session_scope() as db_session:
        result = db_session.query(TestRun).filter(TestRun.name == name, TestRun.suite == suite).all()
        db_session.expunge_all()
        return result
