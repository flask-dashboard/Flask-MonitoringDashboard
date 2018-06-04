"""
    Contains all functions that are used to track the performance of the flask-application.
    See init_measurement() for more detailed info.
"""
import time
from functools import wraps

from flask_monitoringdashboard import user_app
from flask_monitoringdashboard.core.profiler import thread_after_request, threads_before_request
from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    with session_scope() as db_session:
        for rule in get_rules():
            endpoint = get_endpoint_by_name(db_session, rule.endpoint)
            add_decorator(endpoint)


def add_decorator(endpoint):
    """
    Add a wrapper to the Flask-Endpoint based on the monitoring-level.
    :param endpoint: endpoint object
    :return: the wrapper
    """
    func = user_app.view_functions[endpoint.name]

    @wraps(func)
    def wrapper(*args, **kwargs):
        if endpoint.monitor_level == 2 or endpoint.monitor_level == 3:
            threads = threads_before_request(endpoint)
            start_time = time.time()
            result = func(*args, **kwargs)
            stop_time = time.time() - start_time
            for thread in threads:
                thread.stop(stop_time)
        else:
            start_time = time.time()
            result = func(*args, **kwargs)
            stop_time = time.time() - start_time
            thread_after_request(endpoint, stop_time)
        return result

    wrapper.original = func
    user_app.view_functions[endpoint.name] = wrapper

    return wrapper
