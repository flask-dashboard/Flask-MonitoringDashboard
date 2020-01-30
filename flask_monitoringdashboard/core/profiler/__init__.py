import threading

from flask import request

from flask_monitoringdashboard.core.group_by import get_group_by
from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.core.profiler.outlierProfiler import OutlierProfiler
from flask_monitoringdashboard.core.profiler.performanceProfiler import PerformanceProfiler
from flask_monitoringdashboard.core.profiler.stacktraceProfiler import StacktraceProfiler


def start_thread_last_requested(endpoint):
    """
    Starts a thread that updates the last_requested time in the database.
    :param endpoint: Endpoint object
    """
    BaseProfiler(endpoint).start()


def start_performance_thread(endpoint, duration, status_code):
    """
    Starts a thread that updates performance, utilization and last_requested in the database.
    :param endpoint: Endpoint object
    :param duration: duration of the request
    :param status_code: HTTP status code of the request
    """
    ip = request.environ['REMOTE_ADDR']
    group_by = get_group_by()
    PerformanceProfiler(endpoint, ip, duration, group_by, status_code).start()


def start_profiler_thread(endpoint):
    """ Starts a thread that profiles the main thread. """
    current_thread = threading.current_thread().ident
    ip = request.environ['REMOTE_ADDR']
    group_by = get_group_by()
    thread = StacktraceProfiler(current_thread, endpoint, ip, group_by)
    thread.start()
    return thread


def start_outlier_thread(endpoint):
    """ Starts a thread that collects outliers."""
    current_thread = threading.current_thread().ident
    ip = request.environ['REMOTE_ADDR']
    group_by = get_group_by()
    thread = OutlierProfiler(current_thread, endpoint, ip, group_by)
    thread.start()
    return thread


def start_profiler_and_outlier_thread(endpoint):
    """ Starts two threads: PerformanceProfiler and StacktraceProfiler.  """
    import json
    current_thread = threading.current_thread().ident
    ip = request.environ['REMOTE_ADDR']
    group_by = get_group_by()
    request_data = {
        'Headers': request.headers,
        'Params': request.args.to_dict(),
        'Payload': json.loads(request.data) if request.data else {}
    }
    outlier = OutlierProfiler(current_thread, endpoint, ip, group_by)
    thread = StacktraceProfiler(current_thread, endpoint, ip, group_by, request_data, outlier)
    thread.start()
    outlier.start()
    return thread
