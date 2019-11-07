"""
Contains all functions that access a Request object.
"""
import time
from random import sample

from sqlalchemy import and_, func

from flask_monitoringdashboard.database import Request


def get_latencies_in_timeframe(db_session, endpoint_id, start_date, end_date):
    criterion = create_time_based_sample_criterion(start_date, end_date)

    items = db_session.query(Request.duration).filter(Request.endpoint_id == endpoint_id, *criterion).all()

    return [item.duration for item in items]


def get_latencies_sample(db_session, endpoint_id, interval, sample_size=500):
    criterion = create_time_based_sample_criterion(interval.start_date(), interval.end_date())

    dialect = db_session.bind.dialect.name

    if dialect in ['sqlite', 'mysql']:
        order_by = func.random() if dialect == 'sqlite' else func.rand()

        items = db_session.query(Request.duration) \
            .filter(Request.endpoint_id == endpoint_id, *criterion) \
            .order_by(order_by) \
            .limit(sample_size) \
            .all()

        durations = [item.duration for item in items]

        return durations
    else:
        return get_latencies_in_timeframe(db_session, endpoint_id, interval.start_date(), interval.end_date())


def add_request(db_session, duration, endpoint_id, ip, group_by, status_code):
    """ Adds a request to the database. Returns the id.
    :param status_code:  status code of the request
    :param db_session: session for the database
    :param duration: duration of the request
    :param endpoint_id: id of the endpoint
    :param ip: IP address of the requester
    :param group_by: a criteria by which the requests can be grouped
    :return the id of the request after it was stored in the database
    """
    request = Request(
        endpoint_id=endpoint_id,
        duration=duration,
        ip=ip,
        group_by=group_by,
        status_code=status_code,
    )
    db_session.add(request)
    db_session.flush()
    return request.id


def get_date_of_first_request(db_session):
    """ Returns the date (as unix timestamp) of the first request since FMD was deployed.
    :param db_session: session for the database
    :return time of the first request
    """
    result = db_session.query(Request.time_requested).order_by(Request.time_requested).first()
    if result:
        return int(time.mktime(result[0].timetuple()))
    return -1


def create_time_based_sample_criterion(start_date, end_date):
    return and_(Request.time_requested > start_date, Request.time_requested <= end_date)


def get_date_of_first_request_version(db_session, version):
    """ Returns the date (as unix timestamp) of the first request in the current FMD version.
    :param db_session: session for the database
    :param version: version of the dashboard
    :return time of the first request in that version
    """
    result = (
        db_session.query(Request.time_requested)
            .filter(Request.version_requested == version)
            .order_by(Request.time_requested)
            .first()
    )
    if result:
        return int(time.mktime(result[0].timetuple()))
    return -1
