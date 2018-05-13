"""
Contains all functions that operate on the testsGrouped table
"""
from flask_monitoringdashboard.database import TestsGrouped


def reset_tests_grouped(db_session):
    """ Resets the testsGrouped table of the database. """
    db_session.query(TestsGrouped).delete()


def add_tests_grouped(db_session, json):
    """ Adds endpoint - unit tests combinations to the database. """
    for combination in json:
        db_session.add(TestsGrouped(endpoint=combination['endpoint'], test_name=combination['test_name']))


def get_tests_grouped(db_session):
    """ Return all existing endpoint - unit tests combinations. """
    result = db_session.query(TestsGrouped).all()
    db_session.expunge_all()
    return result


def get_endpoint_names(db_session):
    """ Return all existing endpoint names. """
    result = db_session.query(TestsGrouped.endpoint).distinct()
    db_session.expunge_all()
    return [r[0] for r in result]
