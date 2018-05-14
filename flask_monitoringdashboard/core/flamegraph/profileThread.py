import atexit
import collections
import sys
import threading
import time
import traceback


class ProfileThread(threading.Thread):
    def __init__(self, thread_to_monitor, endpoint):
        threading.Thread.__init__(self, name="FlameGraph Thread")
        self._thread_to_monitor = thread_to_monitor
        self._endpoint = endpoint

        self._keeprunning = True
        self._text_dict = {}
        atexit.register(self.stop)

    def run(self):
        while self._keeprunning:
            frame = sys._current_frames()[self._thread_to_monitor]
            self.create_flamegraph_entry(frame)

    def _write_results(self):
        print(self._text_dict.items())

    def create_flamegraph_entry(self, frame):
        in_endpoint_code = False

        for fn, ln, fun, text in traceback.extract_stack(frame)[1:]:
            # fn: filename
            # ln: line number:
            # fun: function name
            # text: source code line
            if self._endpoint is fun:
                in_endpoint_code = True
            if in_endpoint_code:
                self._text_dict[text] = self._text_dict.get(text, 0) + 1

    def stop(self):
        self._keeprunning = False
        self._write_results()
        self._text_dict = {}
        self.join()
