import threading

from flask import request

from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.core.profiler.outlierProfiler import OutlierProfiler
from flask_monitoringdashboard.core.profiler.performanceProfiler import PerformanceProfiler
from flask_monitoringdashboard.core.profiler.stacktraceProfiler import StacktraceProfiler


def threads_before_request(endpoint):
    """
    Starts a thread before the request has been processed
    :param endpoint: endpoint object that is wrapped
    :return: a list with either 1 or 2 threads
    """
    current_thread = threading.current_thread().ident
    ip = request.environ['REMOTE_ADDR']

    if endpoint.monitor_level == 2:
        threads = [StacktraceProfiler(current_thread, endpoint, ip)]
    elif endpoint.monitor_level == 3:
        outlier = OutlierProfiler(current_thread, endpoint)
        threads = [StacktraceProfiler(current_thread, endpoint, ip, outlier), outlier]
    else:
        raise ValueError("MonitorLevel should be 2 or 3.")

    for thread in threads:
        thread.start()
    return threads


def thread_after_request(endpoint, duration):
    """
    Starts a thread after the request has been processed
    :param endpoint: endpoint object that is wrapped
    :param duration: time elapsed for processing the request (in ms)
    """
    if endpoint.monitor_level == 0:
        BaseProfiler(endpoint.id).start()
    elif endpoint.monitor_level == 1:
        ip = request.environ['REMOTE_ADDR']
        PerformanceProfiler(endpoint, ip, duration).start()
    else:
        raise ValueError("MonitorLevel should be 0 or 1.")
