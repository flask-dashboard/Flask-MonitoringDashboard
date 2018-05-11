import datetime

from flask import json
from sqlalchemy import desc

from flask_monitoringdashboard.database import Outlier


def add_outlier(db_session, endpoint, execution_time, stack_info, request):
    """ Collects information (request-parameters, memory, stacktrace) about the request and adds it in the database."""
    outlier = Outlier(endpoint=endpoint, request_values=json.dumps(request.values),
                      request_headers=str(request.headers), request_environment=str(request.environ),
                      request_url=str(request.url), cpu_percent=stack_info.cpu_percent,
                      memory=stack_info.memory, stacktrace=stack_info.stacktrace,
                      execution_time=execution_time, time=datetime.datetime.utcnow())
    db_session.add(outlier)


def get_outliers_sorted(db_session, endpoint, sort_column, offset, per_page):
    """
    :param endpoint: only get outliers from this endpoint
    :param sort_column: column used for sorting the result
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: a list of all outliers of a specific endpoint. The list is sorted based on the column that is given.
    """
    result = db_session.query(Outlier).filter(Outlier.endpoint == endpoint).order_by(desc(sort_column)). \
        offset(offset).limit(per_page).all()
    db_session.expunge_all()
    return result


def get_outliers_cpus(db_session, endpoint):
    """
    :param db_session: the session containing the query
    :param endpoint: only get outliers from this endpoint
    :return: a list of all cpu percentages for outliers of a specific endpoint
    """
    result = db_session.query(Outlier.cpu_percent).filter(Outlier.endpoint == endpoint).all()
    return result


def delete_outliers_without_stacktrace(db_session):
    """
        Remove the outliers which don't have a stacktrace.
        This is possibly due to an error in the outlier functionality
    """
    db_session.query(Outlier).filter(Outlier.stacktrace == '').delete()
