"""
    Contains all functions that are used to track the performance of the flask-application.
    See init_measurement() for more detailed info.
"""
import time
from functools import wraps
from werkzeug.exceptions import HTTPException

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.profiler import (
    start_thread_last_requested,
    start_performance_thread,
    start_outlier_thread,
    start_profiler_and_outlier_thread,
)
from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    with session_scope() as session:
        for rule in get_rules():
            endpoint = get_endpoint_by_name(session, rule.endpoint)
            add_decorator(endpoint)


def add_decorator(endpoint):
    """
    Adds a wrapper to an endpoint in the app, depending on the monitor level.
    :param endpoint: Endpoint object to be monitored
    """
    fun = config.app.view_functions[endpoint.name]
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
    config.app.view_functions[endpoint.name] = wrapper


def is_valid_status_code(status_code):
    """
    Returns whether the input is a valid status code. A status code is valid if it's an integer value and in the
    range [100, 599] :param status_code: :return:
    """
    return type(status_code) == int and 100 <= status_code < 600


def status_code_from_response(result):
    """
    Extracts the status code from the result that was returned from the route handler.

    :param result: The return value of the route handler
    :return:
    """
    if type(result) == str:
        return 200

    status_code = 200  # default

    # Pull it from a tuple
    if isinstance(result, tuple):
        status_code = result[1]
    else:
        # Try to pull it from an object
        try:
            status_code = getattr(result, 'status_code')
        except:
            pass

    if not is_valid_status_code(status_code):
        return 500

    return status_code


def evaluate(route_handler, args, kwargs):
    """
    Invokes the given route handler and extracts the return value, status_code and the exception if it was raised

    :param route_handler:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        result = route_handler(*args, **kwargs)
        status_code = status_code_from_response(result)

        return result, status_code, None
    except HTTPException as e:
        return None, e.code, e
    except Exception as e:
        return None, 500, e


def add_wrapper1(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result, status_code, raised_exception = evaluate(fun, args, kwargs)

        duration = time.time() - start_time
        start_performance_thread(endpoint, duration, status_code)

        if raised_exception:
            raise raised_exception

        return result

    wrapper.original = fun
    config.app.view_functions[endpoint.name] = wrapper


def add_wrapper2(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        outlier = start_outlier_thread(endpoint)
        start_time = time.time()

        result, status_code, raised_exception = evaluate(fun, args, kwargs)

        duration = time.time() - start_time
        outlier.stop(duration, status_code)

        if raised_exception:
            raise raised_exception

        return result

    wrapper.original = fun
    config.app.view_functions[endpoint.name] = wrapper


def add_wrapper3(endpoint, fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        thread = start_profiler_and_outlier_thread(endpoint)
        start_time = time.time()

        result, status_code, raised_exception = evaluate(fun, args, kwargs)

        duration = time.time() - start_time
        thread.stop(duration, status_code)

        if raised_exception:
            raise raised_exception

        return result

    wrapper.original = fun
    config.app.view_functions[endpoint.name] = wrapper
