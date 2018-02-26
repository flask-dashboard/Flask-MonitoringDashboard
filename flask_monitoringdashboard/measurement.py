"""
    Contains all functions that are used to track the performance of the flask-application.
    See init_measurement() for more detailed info.
"""
import time
import datetime
from flask import request
from functools import wraps
from flask_monitoringdashboard import user_app, config
from flask_monitoringdashboard.database.monitor_rules import get_monitor_rules
from flask_monitoringdashboard.database.endpoint import update_last_accessed
from flask_monitoringdashboard.database.function_calls import add_function_call
from flask_monitoringdashboard.database.outlier import add_outlier
from flask_monitoringdashboard.outlier import StackInfo

# count and sum are dicts and used for calculating the averages
endpoint_count = {}
endpoint_sum = {}


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    for rule in get_monitor_rules():
        # add a wrapper for every endpoint
        if rule.endpoint in user_app.view_functions:
            user_app.view_functions[rule.endpoint] = track_performance(user_app.view_functions[rule.endpoint],
                                                                       endpoint=rule.endpoint)

    # filter dashboard rules
    rules = user_app.url_map.iter_rules()
    rules = [r for r in rules if not r.rule.startswith('/' + config.link)
             and not r.rule.startswith('/static-' + config.link)]
    for rule in rules:
        user_app.view_functions[rule.endpoint] = track_last_accessed(user_app.view_functions[rule.endpoint],
                                                                     endpoint=rule.endpoint)


def track_performance(func, endpoint):
    """
    Measure the execution time of a function and store result in the database
    :param func: the function to be measured
    :param endpoint: the name of the endpoint
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # compute average
        average = get_average(endpoint)
        if average:
            average *= config.outlier_detection_constant

            # start a thread to log the stacktrace after 'average' ms
            stack_info = StackInfo(average)

        time1 = time.time()
        result = func(*args, **kwargs)
        time2 = time.time()
        t = (time2 - time1) * 1000
        add_function_call(time=t, endpoint=endpoint, ip=request.environ['REMOTE_ADDR'])

        # outlier detection
        endpoint_count[endpoint] += 1
        endpoint_sum[endpoint] += t
        # check for being an outlier
        if average and float(t) > average:
            add_outlier(endpoint, t, stack_info, request)

        return result

    wrapper.original = func
    return wrapper


def track_last_accessed(func, endpoint):
    """
    Keep track of the last access time of the endpoints. 
    :param func: the function to be measured
    :param endpoint: the name of the endpoint
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        update_last_accessed(endpoint=endpoint, value=datetime.datetime.now())
        return func(*args, **kwargs)

    return wrapper


def get_average(endpoint):
    if endpoint in endpoint_count:
        if endpoint_count[endpoint] < 10:
            return None
    else:
        # initialize endpoint
        endpoint_count[endpoint] = 0
        endpoint_sum[endpoint] = 0
        return None
    return endpoint_sum[endpoint] / endpoint_count[endpoint]
