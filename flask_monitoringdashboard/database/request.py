"""
Contains all functions that access a Request object.
"""

import time

from sqlalchemy import func

from flask_monitoringdashboard.database import Request


def add_request(db_session, duration, endpoint_id, ip):
    """ Adds a request to the database. Returns the id.
    :param db_session: session for the database
    :param duration: duration of the request
    :param endpoint_id: id of the endpoint
    :param ip: IP address of the requester
    :return the id of the request after it was stored in the database
    """
    request = Request(endpoint_id=endpoint_id, duration=duration, ip=ip)
    db_session.add(request)
    db_session.flush()
    return request.id


def get_data_between(db_session, time_from, time_to=None):
    """
        Returns all data in the Request table, for the export data option.
        This function returns all data between time_from and time_to dates. If time_to is not specified, it will
        return all requests after time_from.
    :param db_session: session for the database
    :param time_from: start of the filtering time
    :param time_to: end of the filtering time
    :return list of requests between time_from and time_to
    """
    query = db_session.query(Request).filter(Request.time_requested > time_from)
    if time_to:
        query = query.filter(Request.time_requested <= time_to)
    return query.all()


def get_data(db_session):
    """
    Equivalent function to get_data_from, but returns all data.
    :param db_session: session for the database
    :return list of all requests in the Request table
    """
    return db_session.query(Request).all()


def get_date_of_first_request(db_session):
    """ Returns the date (as unix timestamp) of the first request since FMD was deployed.
    :param db_session: session for the database
    :return time of the first request
    """
    result = db_session.query(Request.time_requested).order_by(Request.time_requested).first()
    if result:
        return int(time.mktime(result[0].timetuple()))
    return -1


def get_date_of_first_request_version(db_session, version):
    """ Returns the date (as unix timestamp) of the first request in the current FMD version.
    :param db_session: session for the database
    :param version: version of the dashboard
    :return time of the first request in that version
    """
    result = db_session.query(Request.time_requested).\
        filter(Request.version_requested == version).\
        order_by(Request.time_requested).first()
    if result:
        return int(time.mktime(result[0].timetuple()))
    return -1


def get_avg_duration(db_session, endpoint_id):
    """ Returns the average duration of all the requests of an endpoint. If there are no requests for that endpoint,
        it returns 0.
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return average duration
    """
    result = db_session.query(func.avg(Request.duration).label('average')). \
        filter(Request.endpoint_id == endpoint_id).one()
    if result[0]:
        return result[0]
    return 0
