import sys
import threading
import traceback
import inspect

from flask_monitoringdashboard import user_app


def append_callgraph(callgraph, encode):
    if callgraph:
        return callgraph + '->' + encode
    return encode


class ProfileThread(threading.Thread):
    def __init__(self, thread_to_monitor, endpoint):
        threading.Thread.__init__(self, name="profileThread")
        self._thread_to_monitor = thread_to_monitor
        self._endpoint = endpoint
        self._total_traces = 0
        self._keeprunning = True
        self._text_dict = {}
        self._h = {}  # dictionary for replacing the filename by an integer

    def run(self):
        while self._keeprunning:
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
                    key = (fn, ln, fun, line, callgraph)
                    if key in self._text_dict:
                        self._text_dict[key] += 1
                    else:
                        self._text_dict[key] = 1
                    encode = self.encode(fn, ln)
                    if encode not in callgraph:
                        callgraph = append_callgraph(callgraph, encode)

    def encode(self, fn, ln):
        return '{}:{}'.format(self.get_index(fn), ln)

    def stop(self):
        self._keeprunning = False
        self._total_traces = sum([v for k, v in self.find_items_with_callgraph(self._text_dict.items(), '')])
        self.print_funcheader()
        self.print_dict()
        self._text_dict.clear()
        self.join()

    def find_items_with_callgraph(self, list, callgraph):
        """ List must be the following: [(key, value), (key, value), ...]"""
        return [(key, value) for key, value in list if key[4] == callgraph]

    def sort(self, list):
        """ Sort on the second element in the key (which is the linenumber) """
        return sorted(list, key=lambda item: item[0][1])

    def print_funcheader(self):
        lines, _ = inspect.getsourcelines(user_app.view_functions[self._endpoint])
        for line in lines:
            line = line.strip()
            print(line)
            if line[:4] == 'def ':
                print(' {:,}'.format(self._total_traces))
                return

    def print_dict(self, callgraph='', indent=1):
        list = self.sort(self.find_items_with_callgraph(self._text_dict.items(), callgraph))
        prefix = '  ' * indent
        if not list:
            return
        for key, count in list:
            print('{}{}: {:,}'.format(prefix, key[3], count))
            self.print_dict(callgraph=append_callgraph(callgraph, self.encode(key[0], key[1])), indent=indent+1)

    def get_index(self, fn):
        if fn in self._h:
            return self._h[fn]
        self._h[fn] = len(self._h)