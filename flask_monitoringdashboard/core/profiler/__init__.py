import threading

from flask import request

from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.core.profiler.performanceProfiler import PerformanceProfiler
from flask_monitoringdashboard.core.profiler.stacktraceProfiler import StacktraceProfiler


def start_profile_thread(endpoint, monitor_level):
    """Start a profiler thread."""
    current_thread = threading.current_thread().ident

    if monitor_level == 0:
        profile_thread = BaseProfiler(current_thread, endpoint)
    elif monitor_level == 1:
        profile_thread = StacktraceProfiler(current_thread, endpoint, request.environ['REMOTE_ADDR'], False)
    elif monitor_level == 2:
        profile_thread = BaseProfiler(current_thread, endpoint)
    elif monitor_level == 3:
        profile_thread = BaseProfiler(current_thread, endpoint)
    else:
        raise ValueError("MonitorLevel should be between 0 and 3.")

    profile_thread.start()
    return profile_thread
