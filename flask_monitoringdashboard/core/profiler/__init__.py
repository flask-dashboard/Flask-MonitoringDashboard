import threading

from flask import request

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


def start_performance_thread(endpoint, duration):
    """
    Starts a thread that updates performance, utilization and last_requested in the database.
    :param endpoint: Endpoint object
    :param duration: duration of the request
    """
    ip = request.environ['REMOTE_ADDR']
    PerformanceProfiler(endpoint, ip, duration).start()


def start_profiler_thread(endpoint):
    """ Starts a thread that monitors the main thread. """
    current_thread = threading.current_thread().ident
    ip = request.environ['REMOTE_ADDR']
    thread = StacktraceProfiler(current_thread, endpoint, ip)
    thread.start()
    return thread


def start_profiler_and_outlier_thread(endpoint):
    """ Starts two threads: PerformanceProfiler and StacktraceProfiler.  """
    current_thread = threading.current_thread().ident
    ip = request.environ['REMOTE_ADDR']
    outlier = OutlierProfiler(current_thread, endpoint)
    thread = StacktraceProfiler(current_thread, endpoint, ip, outlier)
    thread.start()
    outlier.start()
    return thread
