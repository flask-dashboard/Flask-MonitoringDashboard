"""
Contains all functions that operate on the testsGrouped table
"""
from flask_monitoringdashboard.database import session_scope, TestsGrouped


def reset_tests_grouped():
    """ Resets the testsGrouped table of the database. """
    with session_scope() as db_session:
        db_session.query(TestsGrouped).delete()


def add_tests_grouped(json):
    """ Adds endpoint - unit tests combinations to the database. """
    with session_scope() as db_session:
        for combination in json:
            db_session.add(TestsGrouped(endpoint=combination['endpoint'], test_name=combination['test_name']))


def get_tests_grouped():
    """ Return all existing endpoint - unit tests combinations. """
    with session_scope() as db_session:
        result = db_session.query(TestsGrouped).all()
        db_session.expunge_all()
        return result
