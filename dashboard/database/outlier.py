import psutil
import traceback
from flask import json, request
from dashboard.database import session_scope, Outlier


def add_outlier(endpoint):
    """ Collects information (request-parameters, memory, stacktrace) about the request and adds it in the database. """
    with session_scope() as db_session:
        outlier = Outlier(endpoint=endpoint, request_values=json.dumps(request.values),
                          request_headers=str(request.headers), request_environment=str(request.environ),
                          request_url=str(request.url), cpu_percent=psutil.cpu_percent(),
                          memory=str(psutil.virtual_memory()), stacktrace=str(traceback.extract_stack()))
        db_session.add(outlier)


def get_outliers(endpoint):
    """ Returns a list of all outliers of a specific endpoint. """
    with session_scope() as db_session:
        result = db_session.query(Outlier).filter(Outlier.endpoint == endpoint).all()
        db_session.expunge_all()
        return result
