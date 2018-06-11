"""
Contains all functions that access any functionCall-object
"""

import time

from sqlalchemy import func

from flask_monitoringdashboard.database import Request


def add_request(db_session, duration, endpoint_id, ip):
    """ Adds a request to the database. Returns the id."""
    request = Request(endpoint_id=endpoint_id, duration=duration, ip=ip)
    db_session.add(request)
    db_session.flush()
    return request.id


def get_data_between(db_session, time_from, time_to=None):
    """
        Returns all data in the Request table, for the export data option.
        This function returns all data after the time_from date.
    """
    query = db_session.query(Request).filter(Request.time_requested > time_from)
    if time_to:
        query = query.filter(Request.time_requested <= time_to)
    return query.all()


def get_data(db_session):
    """
    Equivalent function to get_data_from, but returns all data.
    :return: all data from the database in the Endpoint-table.
    """
    return db_session.query(Request).all()


def get_date_of_first_request(db_session):
    """ return the date (as unix timestamp) of the first request """
    result = db_session.query(Request.time_requested).order_by(Request.time_requested).first()
    if result:
        return int(time.mktime(result[0].timetuple()))
    return -1


def get_avg_execution_time(db_session, endpoint_id):
    """ Return the average execution time of an endpoint """
    result = db_session.query(func.avg(Request.duration).label('average')). \
        filter(Request.endpoint_id == endpoint_id).one()
    if result[0]:
        return result[0]
    return 0  # default value
