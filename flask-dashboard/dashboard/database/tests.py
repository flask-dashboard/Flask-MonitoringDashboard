"""
Contains all functions that returns results of all tests
"""
from dashboard.database import session_scope, Tests, TestRun
from sqlalchemy import func, desc, text


def get_tests():
    """ Return all existing tests. """
    with session_scope() as db_session:
        result = db_session.query(Tests).all()
        db_session.expunge_all()
        return result


def get_test(name):
    """ Return all existing tests. """
    with session_scope() as db_session:
        result = db_session.query(Tests).filter(Tests.name == name).one()
        db_session.expunge_all()
        return result


def add_test(name):
    """ Add a test to the database. """
    with session_scope() as db_session:
        db_session.add(Tests(name=name))


def update_test(name, run, last_run, succeeded):
    """ Updates values of a test. """
    with session_scope() as db_session:
        db_session.query(Tests).filter(Tests.name == name). \
            update({Tests.run: run, Tests.lastRun: last_run, Tests.succeeded: succeeded})


def reset_run():
    """ Sets all run values to False. """
    with session_scope() as db_session:
        db_session.query(Tests).update({Tests.run: False})


def add_test_result(name, exec_time, time, version):
    """ Add a test result to the database. """
    with session_scope() as db_session:
        db_session.add(TestRun(name=name, execution_time=exec_time, time=time, version=version))


def get_results():
    """ Return all entries of measurements with their average. The results are grouped by their name. """
    with session_scope() as db_session:
        result = db_session.query(TestRun.name,
                                  func.count(TestRun.execution_time).label('count'),
                                  func.avg(TestRun.execution_time).label('average')
                                  ).group_by(TestRun.name).order_by(desc('count')).all()
        db_session.expunge_all()
        return result


def get_line_results():
    return None
    # with session_scope() as db_session:
    #     query = text("""select
    #             datetime(CAST(strftime('%s', time)/3600 AS INT)*3600, 'unixepoch') AS newTime,
    #             avg(execution_time) AS avg,
    #             min(execution_time) as min,
    #             max(execution_time) as max,
    #             count(execution_time) as count
    #         from functioncalls
    #         where endpoint=:val group by newTime""")
    #     result = db_session.execute(query, {'val': endpoint})
    #     data = result.fetchall()
    #     return data
