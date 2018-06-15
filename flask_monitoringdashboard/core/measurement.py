"""
    Contains all functions that are used to track the performance of the flask-application.
    See init_measurement() for more detailed info.
"""
import time
from functools import wraps

from flask_monitoringdashboard import user_app
from flask_monitoringdashboard.core.profiler import start_thread_last_requested, start_performance_thread, \
    start_profiler_thread, start_profiler_and_outlier_thread
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
    Adds a wrapper to an endpoint in the app, depending on the monitor level.
    :param endpoint: Endpoint object to be monitored
    """
    fun = user_app.view_functions[endpoint.name]
    if endpoint.monitor_level == 0:
        add_wrapper0(endpoint, fun)
    elif endpoint.monitor_level == 1:
        add_wrapper1(endpoint, fun)
    elif endpoint.monitor_level == 2:
        add_wrapper2(endpoint, fun)
    elif endpoint.monitor_level == 3:
        add_wrapper3(endpoint, fun)
    else:
        raise ValueError('Incorrect monitoringLevel')


def add_wrapper0(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        result = fun(*args, **kwargs)
        start_thread_last_requested(endpoint)
        return result

    wrapper.original = fun
    user_app.view_functions[endpoint.name] = wrapper


def add_wrapper1(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = fun(*args, **kwargs)
        duration = time.time() - start_time
        start_performance_thread(endpoint, duration)
        return result

    wrapper.original = fun
    user_app.view_functions[endpoint.name] = wrapper


def add_wrapper2(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        thread = start_profiler_thread(endpoint)
        start_time = time.time()
        result = fun(*args, **kwargs)
        duration = time.time() - start_time
        thread.stop(duration)
        return result

    wrapper.original = fun
    user_app.view_functions[endpoint.name] = wrapper


def add_wrapper3(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        thread = start_profiler_and_outlier_thread(endpoint)
        start_time = time.time()
        result = fun(*args, **kwargs)
        duration = time.time() - start_time
        thread.stop(duration)
        return result

    wrapper.original = fun
    user_app.view_functions[endpoint.name] = wrapper
