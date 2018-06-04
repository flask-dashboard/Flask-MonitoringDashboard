from sqlalchemy import desc

from flask_monitoringdashboard.database import Outlier, Request


def add_outlier(db_session, request_id, stack_info):
    """ Collects information (request-parameters, memory, stacktrace) about the request and adds it in the database."""
    from flask import request
    outlier = Outlier(request_id=request_id, request_header=str(request.headers),
                      request_environment=str(request.environ),
                      request_url=str(request.url), cpu_percent=stack_info.cpu_percent,
                      memory=stack_info.memory, stacktrace=stack_info.stacktrace)
    db_session.add(outlier)


def get_outliers_sorted(db_session, endpoint_id, sort_column, offset, per_page):
    """
    :param endpoint_id: endpoint_id for filtering the requests
    :param sort_column: column used for sorting the result
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: a list of all outliers of a specific endpoint. The list is sorted based on the column that is given.
    """
    result = db_session.query(Request.outlier).filter(Request.endpoint_id == endpoint_id).order_by(desc(sort_column)). \
        offset(offset).limit(per_page).all()
    db_session.expunge_all()
    return result


def get_outliers_cpus(db_session, endpoint_id):
    """
    :param db_session: the session containing the query
    :param endpoint_id: endpoint_id for filtering the requests
    :return: a list of all cpu percentages for outliers of a specific endpoint
    """
    return db_session.query(Request.outlier.cpu_percent).filter(Request.endpoint_id == endpoint_id).all()


def delete_outliers_without_stacktrace(db_session):
    """
        Remove the outliers which don't have a stacktrace.
        This is possibly due to an error in the outlier functionality
    """
    db_session.query(Outlier).filter(Outlier.stacktrace == '').delete()
