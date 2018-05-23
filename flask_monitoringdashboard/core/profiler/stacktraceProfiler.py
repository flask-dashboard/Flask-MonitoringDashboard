import inspect
import sys
import traceback
from collections import defaultdict

from flask_monitoringdashboard import user_app
from flask_monitoringdashboard.core.profiler import PerformanceProfiler
from flask_monitoringdashboard.database.execution_path_line import add_execution_path_line

FILE_SPLIT = '->'


class StacktraceProfiler(PerformanceProfiler):

    def __init__(self, thread_to_monitor, endpoint, ip, only_outliers):
        super(StacktraceProfiler, self).__init__(thread_to_monitor, endpoint, ip)
        self.only_outliers = only_outliers
        self._text_dict = defaultdict(int)
        self._h = {}  # dictionary for replacing the filename by an integer
        self._lines_body = []

    def _run_cycle(self):
        frame = sys._current_frames()[self._thread_to_monitor]
        in_endpoint_code = False
        encoded_path = ''
        for fn, ln, fun, line in traceback.extract_stack(frame):
            # fn: filename
            # ln: line number
            # fun: function name
            # text: source code line
            if self._endpoint is fun:
                in_endpoint_code = True
            if in_endpoint_code:
                key = (fn, ln, fun, line, encoded_path)  # quintuple
                self._text_dict[key] += 1
                encode = self.encode(fn, ln)
                if encode not in encoded_path:
                    encoded_path = append_to_encoded_path(encoded_path, encode)

    def _on_thread_stopped(self, db_session):
        super(StacktraceProfiler, self)._on_thread_stopped(db_session)

        if self.only_outliers:
            pass
            # TODO: check if req is outlier
            # if outlier store to db
        else:
            total_traces = sum([v for k, v in filter_on_encoded_path(self._text_dict.items(), '')])
            line_number = 0
            for line in self.get_funcheader():
                add_execution_path_line(db_session, self._request_id, line_number, 0, line, total_traces)
                line_number += 1
            self.order_text_dict()

            for (line, path, val) in self._lines_body:
                add_execution_path_line(db_session, self._request_id, line_number, get_indent(path), line, val)
                line_number += 1
            self._text_dict.clear()

    def get_funcheader(self):
        lines_returned = []
        lines, _ = inspect.getsourcelines(user_app.view_functions[self._endpoint])
        for line in lines:
            lines_returned.append(line.strip())
            if line.strip()[:4] == 'def ':
                return lines_returned

    def order_text_dict(self, encoded_path=''):
        """
        Finds the order of self._text_dict and assigns this order to self._lines_body
        :param encoded_path: used to filter the results
        :return:
        """
        list = sorted(filter_on_encoded_path(self._text_dict.items(), encoded_path), key=lambda item: item[0][1])
        if not list:
            return
        for key, count in list:
            self._lines_body.append((key[3], key[4], count))
            self.order_text_dict(encoded_path=append_to_encoded_path(encoded_path, self.encode(key[0], key[1])))

    def encode(self, fn, ln):
        return str(self.get_index(fn)) + ':' + str(ln)

    def get_index(self, fn):
        if fn in self._h:
            return self._h[fn]
        self._h[fn] = len(self._h)


def get_indent(string):
    if string:
        return len(string.split(FILE_SPLIT)) + 1
    return 1


def filter_on_encoded_path(list, encoded_path):
    """ List must be the following: [(key, value), (key, value), ...]"""
    return [(key, value) for key, value in list if key[4] == encoded_path]


def append_to_encoded_path(callgraph, encode):
    if callgraph:
        return callgraph + FILE_SPLIT + encode
    return encode
