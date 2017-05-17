import time
import datetime
from functools import wraps
from dashboard import user_app
from dashboard.database.monitor_rules import get_monitor_rules
from dashboard.database.endpoint import update_last_accessed
from dashboard.database.function_calls import add_function_call


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    for rule in get_monitor_rules():
        user_app.view_functions[rule.endpoint] = track_performance(user_app.view_functions[rule.endpoint])

    for rule in user_app.url_map.iter_rules():
        user_app.view_functions[rule.endpoint] = track_last_accessed(user_app.view_functions[rule.endpoint])


def track_performance(func):
    """
    Measure the execution time of a function and store result in the database
    :param func: the function to be measured
    :return: 
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        time1 = time.time()
        result = func(*args, **kwargs)
        time2 = time.time()
        t = (time2-time1)*1000
        add_function_call(time=t, endpoint=func.__name__)
        return result
    wrapper.original = func
    return wrapper


def track_last_accessed(func):
    """ Keep track of the last access time of the endpoints. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = datetime.datetime.now()
        update_last_accessed(endpoint=func.__name__, value=t)
        result = func(*args, **kwargs)
        return result
    return wrapper
