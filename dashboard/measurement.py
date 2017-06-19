"""
    Contains all functions that are used to track the performance of the flask-application.
    See init_measurement() for more detailed info.
"""
import time
import datetime
from functools import wraps
from dashboard import user_app, config
from dashboard.database.monitor_rules import get_monitor_rules
from dashboard.database.endpoint import update_last_accessed
from dashboard.database.function_calls import add_function_call
from dashboard.database.outlier import add_outlier

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
        # init dictionary for every endpoint
        endpoint_count[rule.endpoint] = 0
        endpoint_sum[rule.endpoint] = 0
        # add a wrapper for every endpoint
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
        time1 = time.time()
        result = func(*args, **kwargs)
        time2 = time.time()
        t = (time2-time1)*1000
        add_function_call(time=t, endpoint=endpoint)

        endpoint_count[endpoint] += 1
        endpoint_sum[endpoint] += t
        # check for being an outlier
        if float(t) > 2.5 * get_average(endpoint):
            # TODO: update 2.5 with variable
            add_outlier(endpoint, t)

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
    return endpoint_sum[endpoint] / endpoint_count[endpoint]
