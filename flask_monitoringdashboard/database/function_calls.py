"""
Contains all functions that access any functionCall-object
"""

import time

from sqlalchemy import distinct

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import FunctionCall


def add_function_call(db_session, execution_time, endpoint, ip):
    """ Add a measurement to the database. """
    db_session.add(FunctionCall(endpoint=endpoint, execution_time=execution_time, version=config.version, ip=ip))


def get_data_between(db_session, time_from, time_to=None):
    """
        Returns all data in the FunctionCall table, for the export data option.
        This function returns all data after the time_from date.
    """
    query = db_session.query(FunctionCall).filter(FunctionCall.time > time_from)
    if time_to:
        query = query.filter(FunctionCall.time <= time_to)
    return query.all()


def get_data(db_session):
    """
    Equivalent function to get_data_from, but returns all data.
    :return: all data from the database in the Endpoint-table.
    """
    return db_session.query(FunctionCall).all()


def get_endpoints(db_session):
    """ Returns the name of all endpoints from the database """
    result = db_session.query(distinct(FunctionCall.endpoint)).order_by(FunctionCall.endpoint).all()
    db_session.expunge_all()
    return [r[0] for r in result]  # unpack tuple result


def get_date_of_first_request(db_session):
    """ return the date (as unix timestamp) of the first request """
    result = db_session.query(FunctionCall.time).order_by(FunctionCall.time).first()
    if result:
        return int(time.mktime(result[0].timetuple()))
    return -1
