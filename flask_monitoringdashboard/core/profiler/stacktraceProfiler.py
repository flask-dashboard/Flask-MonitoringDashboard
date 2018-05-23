import inspect
import sys
import traceback
from collections import defaultdict

from flask_monitoringdashboard import user_app
from flask_monitoringdashboard.core.profiler import PerformanceProfiler
from flask_monitoringdashboard.database.execution_path_line import add_execution_path_line


class StacktraceProfiler(PerformanceProfiler):

    def __init__(self, thread_to_monitor, endpoint, ip, only_outliers):
        super(StacktraceProfiler, self).__init__(thread_to_monitor, endpoint, ip)
        self.only_outliers = only_outliers
        self._text_dict = defaultdict(int)
        self._h = {}  # dictionary for replacing the filename by an integer

    def _run_cycle(self):
        frame = sys._current_frames()[self._thread_to_monitor]
        in_endpoint_code = False
        callgraph = ''
        for fn, ln, fun, line in traceback.extract_stack(frame):
            # fn: filename
            # ln: line number
            # fun: function name
            # text: source code line
            if self._endpoint is fun:
                in_endpoint_code = True
            if in_endpoint_code:
                key = (fn, ln, fun, line, callgraph)  # quintuple
                self._text_dict[key] += 1
                encode = self.encode(fn, ln)
                if encode not in callgraph:
                    callgraph = append_callgraph(callgraph, encode)

    def _on_thread_stopped(self, db_session):
        super(StacktraceProfiler, self)._on_thread_stopped(db_session)
        print("----------%d" % self._request_id)

        if self.only_outliers:
            pass
            # TODO: check if req is outlier
            # if outlier store to db
        else:
            total_traces = sum([v for k, v in find_items_with_callgraph(self._text_dict.items(), '')])
            self.print_funcheader(total_traces)
            self.print_dict()
            for (key, val) in self._text_dict.items():
                print("%s----%s" %(key, val))
                add_execution_path_line(db_session, self._request_id, key[1], len(key[4].split('->')),
                                        key[0] + ":" + key[2] + ":" + key[3], val)
            self._text_dict.clear()

    def print_funcheader(self, total_traces):
        lines, _ = inspect.getsourcelines(user_app.view_functions[self._endpoint])
        for line in lines:
            line = line.strip()
            print(line)
            if line[:4] == 'def ':
                print(' {:,}'.format(total_traces))
                return

    def print_dict(self, callgraph='', indent=1):
        list = sorted(find_items_with_callgraph(self._text_dict.items(), callgraph), key=lambda item: item[0][1])
        prefix = '  ' * indent
        if not list:
            return
        for key, count in list:
            print('{}{}: {:,}'.format(prefix, key[3], count))
            self.print_dict(callgraph=append_callgraph(callgraph, self.encode(key[0], key[1])), indent=indent + 1)

    def encode(self, fn, ln):
        return str(self.get_index(fn)) + ':' + str(ln)

    def get_index(self, fn):
        if fn in self._h:
            return self._h[fn]
        self._h[fn] = len(self._h)


def find_items_with_callgraph(list, callgraph):
    """ List must be the following: [(key, value), (key, value), ...]"""
    return [(key, value) for key, value in list if key[4] == callgraph]


def append_callgraph(callgraph, encode):
    if callgraph:
        return callgraph + '->' + encode
    return encode
