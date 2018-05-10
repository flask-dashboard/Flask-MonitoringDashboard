"""
    Contains all functions that are used to track the performance of the flask-application.
    See init_measurement() for more detailed info.
"""
import datetime
import time
import traceback
from functools import wraps

from flask import request

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.outlier import StackInfo
from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed, get_monitor_rule
from flask_monitoringdashboard.database.function_calls import add_function_call
from flask_monitoringdashboard.database.outlier import add_outlier

# count and sum are dicts and used for calculating the averages
endpoint_count = {}
endpoint_sum = {}

MIN_NUM_REQUESTS = 10


def init_measurement():
    """
    This should be added to the list of functions that are executed before the first request.
    This function is used in the config-method in __init__ of this folder
    It adds wrappers to the endpoints for tracking their performance and last access times.
    """
    from flask_monitoringdashboard import user_app
    with session_scope() as db_session:
        for rule in get_rules():
            end = rule.endpoint
            db_rule = get_monitor_rule(db_session, end)
            user_app.view_functions[end] = track_last_accessed(user_app.view_functions[end], end)
            if db_rule.monitor:
                user_app.view_functions[end] = track_performance(user_app.view_functions[end], end)


def track_performance(func, endpoint):
    """
    Measure the execution time of a function and store result in the database
    :param func: the function to be measured
    :param endpoint: the name of the endpoint
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # compute average
            average = get_average(endpoint)

            stack_info = None

            if average:
                average *= config.outlier_detection_constant

                # start a thread to log the stacktrace after 'average' ms
                stack_info = StackInfo(average)

            time1 = time.time()
            result = func(*args, **kwargs)

            if stack_info:
                stack_info.stop()

            time2 = time.time()
            t = (time2 - time1) * 1000
            with session_scope() as db_session:
                add_function_call(db_session, execution_time=t, endpoint=endpoint, ip=request.environ['REMOTE_ADDR'])

            # outlier detection
            endpoint_count[endpoint] = endpoint_count.get(endpoint, 0) + 1
            endpoint_sum[endpoint] = endpoint_sum.get(endpoint, 0) + t

            if stack_info:
                with session_scope() as db_session:
                    add_outlier(db_session, endpoint, t, stack_info, request)

            return result
        except:
            traceback.print_exc()
            # Execute the endpoint that was called, even if the tracking fails.
            return func(*args, **kwargs)

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
        try:
            with session_scope() as db_session:
                update_last_accessed(db_session, endpoint=endpoint, value=datetime.datetime.utcnow())
        except:
            traceback.print_exc()

        # Execute the endpoint that was called, even if the tracking fails.
        return func(*args, **kwargs)

    return wrapper


def get_average(endpoint):
    if not config.outliers_enabled:
        return None

    if endpoint in endpoint_count:
        if endpoint_count[endpoint] < MIN_NUM_REQUESTS:
            return None
    else:
        # initialize endpoint
        endpoint_count[endpoint] = 0
        endpoint_sum[endpoint] = 0
        return None
    return endpoint_sum[endpoint] / endpoint_count[endpoint]
