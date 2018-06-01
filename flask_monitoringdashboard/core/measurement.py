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
from flask_monitoringdashboard.database.endpoint import get_monitor_rule


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    with session_scope() as db_session:
        for rule in get_rules():
            db_rule = get_monitor_rule(db_session, rule.endpoint)
            add_decorator(rule.endpoint, db_rule.monitor_level)


def add_decorator(endpoint, monitor_level):
    """
    Add a wrapper to the Flask-Endpoint based on the monitoring-level.
    :param endpoint: name of the endpoint as a string
    :param monitor_level: int with the wrapper that should be added. This value is either 0, 1, 2 or 3.
    :return: the wrapper
    """
    func = user_app.view_functions[endpoint]

    @wraps(func)
    def wrapper(*args, **kwargs):
        if monitor_level == 2 or monitor_level == 3:
            threads = threads_before_request(endpoint, monitor_level)
            start_time = time.time()
            result = func(*args, **kwargs)
            stop_time = time.time() - start_time
            for thread in threads:
                thread.stop(stop_time)
        else:
            start_time = time.time()
            result = func(*args, **kwargs)
            stop_time = time.time() - start_time
            thread_after_request(endpoint, monitor_level, stop_time)
        return result

    wrapper.original = func
    user_app.view_functions[endpoint] = wrapper

    return wrapper
