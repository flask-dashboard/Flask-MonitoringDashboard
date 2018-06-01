import datetime
import inspect
import sys
import threading
import traceback
from collections import defaultdict

from flask_monitoringdashboard import user_app
from flask_monitoringdashboard.core.profiler.pathHash import PathHash
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed
from flask_monitoringdashboard.database.execution_path_line import add_execution_path_line
from flask_monitoringdashboard.database.request import add_request


class StacktraceProfiler(threading.Thread):
    """
    Used for profiling the performance per line code.
    """

    def __init__(self, thread_to_monitor, endpoint, ip):
        threading.Thread.__init__(self)
        self._keeprunning = True
        self._thread_to_monitor = thread_to_monitor
        self._endpoint = endpoint
        self._ip = ip
        self._duration = 0
        self._histogram = defaultdict(int)
        self._path_hash = PathHash()
        self._lines_body = []

    def run(self):
        """
        Continuously takes a snapshot from the stacktrace (only the main-thread). Filters everything before the
        endpoint has been called (i.e. the Flask library).
        Directly computes the histogram, since this is more efficient for storingpo
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
                # text: source code line
                if self._endpoint is fun:
                    in_endpoint_code = True
                if in_endpoint_code:
                    key = (self._path_hash.get_path(fn, ln), line)
                    self._histogram[key] += 1
        self._on_thread_stopped()

    def stop(self, duration):
        self._duration = duration * 1000
        self._keeprunning = False

    def _on_thread_stopped(self):
        self._order_histogram()
        with session_scope() as db_session:
            update_last_accessed(db_session, endpoint=self._endpoint, value=datetime.datetime.utcnow())
            request_id = add_request(db_session, execution_time=self._duration, endpoint=self._endpoint, ip=self._ip)
            self.insert_lines_db(db_session, request_id)

    def get_funcheader(self):
        lines_returned = []
        lines, _ = inspect.getsourcelines(user_app.view_functions[self._endpoint])
        for line in lines:
            lines_returned.append(line.strip())
            if line.strip()[:4] == 'def ':
                return lines_returned

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
        line_number = 0
        for line in self.get_funcheader():
            add_execution_path_line(db_session, request_id, line_number, 0, line, total_traces)
            line_number += 1

        for (key, val) in self._lines_body:
            path, text = key
            indent = self._path_hash.get_indent(path)
            add_execution_path_line(db_session, request_id, line_number, indent, text, val)
            line_number += 1

    def _get_order(self, path):
        indent = self._path_hash.get_indent(path) + 1
        return sorted([row for row in self._histogram.items()
                       if row[0][0][:len(path)] == path and indent == self._path_hash.get_indent(row[0][0])],
                      key=lambda row: row[0][0])
