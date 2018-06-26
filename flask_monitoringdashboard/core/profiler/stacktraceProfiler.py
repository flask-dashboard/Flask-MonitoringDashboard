import inspect
import sys
import threading
import time
import traceback
from collections import defaultdict

from flask_monitoringdashboard import user_app, config
from flask_monitoringdashboard.core.logger import log
from flask_monitoringdashboard.core.profiler.util import order_histogram
from flask_monitoringdashboard.core.profiler.util.pathHash import PathHash
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed
from flask_monitoringdashboard.database.request import add_request
from flask_monitoringdashboard.database.stack_line import add_stack_line


FILENAME = 'flask_monitoringdashboard/core/measurement.py'
FILENAME_LEN = len(FILENAME)

class StacktraceProfiler(threading.Thread):
    """
    Used for profiling the performance per line code.
    This is used when monitoring-level == 2 and monitoring-level == 3
    """

    def __init__(self, thread_to_monitor, endpoint, ip, outlier_profiler=None):
        threading.Thread.__init__(self)
        self._keeprunning = True
        self._thread_to_monitor = thread_to_monitor
        self._endpoint = endpoint
        self._ip = ip
        self._duration = 0
        self._histogram = defaultdict(float)
        self._path_hash = PathHash()
        self._lines_body = []
        self._total = 0
        self._outlier_profiler = outlier_profiler

    def run(self):
        """
        Continuously takes a snapshot from the stacktrace (only the main-thread). Filters everything before the
        endpoint has been called (i.e. the Flask library).
        Directly computes the histogram, since this is more efficient for performance
        :return:
        """
        current_time = time.time()
        while self._keeprunning:
            newcurrent_time = time.time()
            duration = newcurrent_time - current_time
            current_time = newcurrent_time

            try:
                frame = sys._current_frames()[self._thread_to_monitor]
            except KeyError:
                log('Can\'t get the stacktrace of the main thread. Stopping StacktraceProfiler')
                break
            in_endpoint_code = False
            self._path_hash.set_path('')
            # filename, line number, function name, source code line
            for fn, ln, fun, line in traceback.extract_stack(frame):
                if self._endpoint.name == fun:
                    in_endpoint_code = True
                if in_endpoint_code:
                    key = (self._path_hash.get_path(fn, ln), fun, line)
                    self._histogram[key] += duration
                if len(fn) > FILENAME_LEN and fn[-FILENAME_LEN:] == FILENAME and fun == "wrapper":
                    in_endpoint_code = True
            if in_endpoint_code:
                self._total += duration

            elapsed = time.time() - current_time
            if config.sampling_period > elapsed:
                time.sleep(config.sampling_period - elapsed)

        self._on_thread_stopped()

    def stop(self, duration):
        self._duration = duration * 1000
        if self._outlier_profiler:
            self._outlier_profiler.stop()
        self._keeprunning = False

    def _on_thread_stopped(self):
        with session_scope() as db_session:
            update_last_accessed(db_session, endpoint_name=self._endpoint.name)
            request_id = add_request(db_session, duration=self._duration, endpoint_id=self._endpoint.id, ip=self._ip)
            self._lines_body = order_histogram(self._histogram.items())
            self.insert_lines_db(db_session, request_id)

        if self._outlier_profiler:
            self._outlier_profiler.add_outlier(request_id)

    def insert_lines_db(self, db_session, request_id):
        position = 0
        for code_line in self.get_funcheader():
            add_stack_line(db_session, request_id, position=position, indent=0, duration=self._duration,
                           code_line=code_line)
            position += 1

        for key, val in self._lines_body:
            path, fun, line = key
            fn, ln = self._path_hash.get_last_fn_ln(path)
            indent = self._path_hash.get_indent(path)
            duration = val * self._duration / self._total
            add_stack_line(db_session, request_id, position=position, indent=indent, duration=duration,
                           code_line=(fn, ln, fun, line))
            position += 1

    def get_funcheader(self):
        lines_returned = []
        try:
            fun = user_app.view_functions[self._endpoint.name]
        except AttributeError:
            fun = None
        if hasattr(fun, 'original'):
            original = fun.original
            fn = inspect.getfile(original)
            lines, ln = inspect.getsourcelines(original)
            count = 0
            for line in lines:
                lines_returned.append((fn, ln + count, 'None', line.strip()))
                count += 1
                if line.strip()[:4] == 'def ':
                    return lines_returned
        raise ValueError('Cannot retrieve the function header')
