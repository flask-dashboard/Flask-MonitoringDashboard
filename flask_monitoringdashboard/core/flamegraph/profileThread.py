import atexit
import collections
import sys
import threading
import time
import traceback


class ProfileThread(threading.Thread):
    def __init__(self, thread_to_monitor):
        threading.Thread.__init__(self, name="FlameGraph Thread")
        self._thread_to_monitor = thread_to_monitor

        self._keeprunning = True
        self._text_dict = {}
        atexit.register(self.stop)

    def run(self):
        current_time = time.time()
        elapsed = 0.0
        while self._keeprunning:
            elapsed += 0.100
            frame = sys._current_frames()[self._thread_to_monitor]
            self.create_flamegraph_entry(frame)
            secs_passed = time.time() - current_time
            if elapsed > secs_passed:
                time.sleep(elapsed - secs_passed)

    def _write_results(self):
        print(self._text_dict.items())

    def create_flamegraph_entry(self, frame):
        wrapper_code = 'func(*args, **kwargs)'  # defined in flask_monitoringdashboard/core/measurement.py
        after_wrapper = False

        for fn, ln, fun, text in traceback.extract_stack(frame)[1:]:
            # fn: filename
            # ln: line number:
            # fun: function name
            # text: source code line
            if wrapper_code in text:
                after_wrapper = True
            elif after_wrapper and wrapper_code not in text:
                self._text_dict[text] = self._text_dict.get(text, 0) + 1

    def stop(self):
        self._keeprunning = False
        self._write_results()
        self._text_dict = {}
        self.join()
