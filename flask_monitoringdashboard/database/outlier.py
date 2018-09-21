from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from flask_monitoringdashboard.database import Outlier, Request


def add_outlier(db_session, request_id, cpu_percent, memory, stacktrace, request):
    """
    Adds an Outlier object in the database.
    :param db_session: session for the database
    :param request_id: id of the request
    :param cpu_percent: cpu load of the server when processing the request
    :param memory: memory load of the server when processing the request
    :param stacktrace: stack trace of the request
    :param request: triple containing the headers, environment and url
    """
    headers, environ, url = request
    outlier = Outlier(request_id=request_id, request_header=headers,
                      request_environment=environ,
                      request_url=url, cpu_percent=cpu_percent,
                      memory=memory, stacktrace=stacktrace)
    db_session.add(outlier)


def get_outliers_sorted(db_session, endpoint_id, offset, per_page):
    """
    Gets a list of Outlier objects for a certain endpoint, sorted by most recent request time
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint for filtering the requests
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return list of Outlier objects of a specific endpoint
    """
    result = db_session.query(Outlier).\
        join(Outlier.request). \
        options(joinedload(Outlier.request).joinedload(Request.endpoint)). \
        filter(Request.endpoint_id == endpoint_id). \
        order_by(desc(Request.time_requested)). \
        offset(offset).limit(per_page).all()
    db_session.expunge_all()
    return result


def get_outliers_cpus(db_session, endpoint_id):
    """
    Gets list of CPU loads of all outliers of a certain endpoint
    :param db_session: session for the database
    :param endpoint_id: id of the endpoint
    :return list of cpu percentages as strings
    """
    outliers = db_session.query(Outlier.cpu_percent).\
        join(Outlier.request).\
        filter(Request.endpoint_id == endpoint_id).all()
    return [outlier[0] for outlier in outliers]


def get_all_outliers(db_session):
    """
    :param db_session: session for the database
    :return list of all outliers in the Outlier table
    """
    return db_session.query(Outlier).all()
