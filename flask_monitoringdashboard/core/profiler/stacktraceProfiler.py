import inspect
import sys
import threading
import traceback
from collections import defaultdict

from flask_monitoringdashboard import user_app
from flask_monitoringdashboard.core.profiler.pathHash import PathHash
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed
from flask_monitoringdashboard.database.request import add_request
from flask_monitoringdashboard.database.stack_line import add_stack_line


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
        self._histogram = defaultdict(int)
        self._path_hash = PathHash()
        self._lines_body = []
        self._outlier_profiler = outlier_profiler

    def run(self):
        """
        Continuously takes a snapshot from the stacktrace (only the main-thread). Filters everything before the
        endpoint has been called (i.e. the Flask library).
        Directly computes the histogram, since this is more efficient for performance
        :return:
        """
        while self._keeprunning:
            frame = sys._current_frames()[self._thread_to_monitor]
            in_endpoint_code = False
            self._path_hash.set_path('')
            for fn, ln, fun, line in traceback.extract_stack(frame):
                # fn: filename
                # ln: line number
                # fun: function name
                # line: source code line
                if self._endpoint.name == fun:
                    in_endpoint_code = True
                if in_endpoint_code:
                    key = (self._path_hash.get_path(fn, ln), fun, line)
                    self._histogram[key] += 1
        self._on_thread_stopped()

    def stop(self, duration):
        self._duration = duration * 1000
        self._keeprunning = False

    def _on_thread_stopped(self):
        with session_scope() as db_session:
            update_last_accessed(db_session, endpoint_name=self._endpoint.name)
            request_id = add_request(db_session, duration=self._duration, endpoint_id=self._endpoint.id, ip=self._ip)
            self._outlier_profiler.set_request_id(db_session, request_id)
            self._order_histogram()
            self.insert_lines_db(db_session, request_id)

    def get_funcheader(self):
        lines_returned = []
        fun = user_app.view_functions[self._endpoint.name]
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

    def _order_histogram(self, path=''):
        """
        Finds the order of self._text_dict and assigns this order to self._lines_body
        :param path: used to filter the results
        :return:
        """
        for key, count in self._get_order(path):
            self._lines_body.append((key, count))
            self._order_histogram(path=key[0])

    def insert_lines_db(self, db_session, request_id):
        total_traces = sum([v for k, v in self._get_order('')])
        position = 0
        for code_line in self.get_funcheader():
            add_stack_line(db_session, request_id, position=position, indent=0, duration=self._duration,
                           code_line=code_line)
            position += 1

        for key, val in self._lines_body:
            path, fun, line = key
            fn, ln = self._path_hash.get_last_fn_ln(path)
            indent = self._path_hash.get_indent(path)
            duration = val * self._duration / total_traces
            add_stack_line(db_session, request_id, position=position, indent=indent, duration=duration,
                           code_line=(fn, ln, fun, line))
            position += 1

    def _get_order(self, path):
        indent = self._path_hash.get_indent(path) + 1
        return sorted([row for row in self._histogram.items()
                       if row[0][0][:len(path)] == path and indent == self._path_hash.get_indent(row[0][0])],
                      key=lambda row: row[0][0])
