from sqlalchemy import desc

from flask_monitoringdashboard.database import Outlier, Request


def add_outlier(db_session, request_id, cpu_percent, memory, stacktrace, request):
    """ Collects information (request-parameters, memory, stacktrace) about the request and adds it in the database."""
    headers, environ, url = request
    outlier = Outlier(request_id=request_id, request_header=str(request.headers),
                      request_environment=str(request.environ),
                      request_url=str(request.url), cpu_percent=cpu_percent,
                      memory=memory, stacktrace=stacktrace)
    db_session.add(outlier)


def get_outliers_sorted(db_session, endpoint_id, offset, per_page):
    """
    :param endpoint_id: endpoint_id for filtering the requests
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: a list of all outliers of a specific endpoint. The list is sorted based on the column that is given.
    """
    result = db_session.query(Request.outlier).\
        filter(Request.endpoint_id == endpoint_id).\
        order_by(desc(Request.time_requested)). \
        offset(offset).limit(per_page).all()
    db_session.expunge_all()
    return result


def get_outliers_cpus(db_session, endpoint_id):
    """
    :param db_session: the session containing the query
    :param endpoint_id: endpoint_id for filtering the requests
    :return: a list of all cpu percentages for outliers of a specific endpoint
    """
    outliers = db_session.query(Request.outlier).filter(Request.endpoint_id == endpoint_id).all()
    return [outlier.cpu_percent for outlier in outliers]
