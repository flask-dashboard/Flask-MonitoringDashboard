import datetime
from flask import json
from flask_monitoringdashboard.database import session_scope, Outlier


def add_outlier(endpoint, execution_time, stack_info, request):
    """ Collects information (request-parameters, memory, stacktrace) about the request and adds it in the database. """
    with session_scope() as db_session:
        outlier = Outlier(endpoint=endpoint, request_values=json.dumps(request.values),
                          request_headers=str(request.headers), request_environment=str(request.environ),
                          request_url=str(request.url), cpu_percent=stack_info.cpu_percent,
                          memory=stack_info.memory, stacktrace=stack_info.stacktrace,
                          execution_time=execution_time, time=datetime.datetime.now())
        db_session.add(outlier)


def get_outliers(endpoint):
    """ Returns a list of all outliers of a specific endpoint. """
    with session_scope() as db_session:
        result = db_session.query(Outlier).filter(Outlier.endpoint == endpoint).all()
        db_session.expunge_all()
        return result
