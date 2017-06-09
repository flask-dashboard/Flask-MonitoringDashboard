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


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    # TODO: Uncomment this. Was commented for testing using zeeguu collected data.
    # for rule in get_monitor_rules():
    #     user_app.view_functions[rule.endpoint] = track_performance(user_app.view_functions[rule.endpoint],
    #                                                                endpoint=rule.endpoint)

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
