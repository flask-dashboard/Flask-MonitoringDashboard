import sys
import threading
import traceback


class ProfileThread(threading.Thread):
    def __init__(self, thread_to_monitor, endpoint):
        threading.Thread.__init__(self, name="profileThread")
        self._thread_to_monitor = thread_to_monitor
        self._endpoint = endpoint
        self._keeprunning = True
        self._text_dict = {}

    def run(self):
        while self._keeprunning:
            frame = sys._current_frames()[self._thread_to_monitor]
            in_endpoint_code = False

            for fn, ln, fun, text in traceback.extract_stack(frame):
                # fn: filename
                # ln: line number:
                # fun: function name
                # text: source code line
                if self._endpoint is fun:
                    in_endpoint_code = True
                if in_endpoint_code:
                    key = (fn, ln, fun, text)
                    if key in self._text_dict:
                        self._text_dict[key] += 1
                    else:
                        self._text_dict[key] = 1

    def stop(self):
        self._keeprunning = False
        for (fn, ln, _, _), value in self._text_dict.items():
            f = open(fn)
            lines = f.readlines()
            print('{}: {}'.format(lines[ln-1].strip(), value))
        self._text_dict.clear()
        self.join()
