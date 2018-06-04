import sys
import threading
import time
import traceback

import psutil

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.request import get_avg_execution_time


class OutlierProfiler(threading.Thread):
    """
    Used for collecting additional information if the request is an outlier
    """

    def __init__(self, current_thread, endpoint):
        threading.Thread.__init__(self)
        self._current_thread = current_thread
        self._endpoint = endpoint
        self._stopped = False

    def run(self):
        # sleep for average * ODC ms
        with session_scope() as db_session:
            average = get_avg_execution_time(db_session, self._endpoint) * config.outlier_detection_constant
        time.sleep(average / 1000.0)
        if not self._stopped:
            stack_list = []
            frame = sys._current_frames()[self._current_thread]
            in_endpoint_code = False
            for fn, ln, fun, line in traceback.extract_stack(frame):
                # fn: filename
                # ln: line number
                # fun: function name
                # text: source code line
                if self._endpoint is fun:
                    in_endpoint_code = True
                if in_endpoint_code:
                    stack_list.append('File: "{}", line {}, in "{}": "{}"'.format(fn, ln, fun, line))

            # Set the values in the object
            stacktrace = '<br />'.join(stack_list)
            cpu_percent = str(psutil.cpu_percent(interval=None, percpu=True))
            memory = str(psutil.virtual_memory())

            # print(stacktrace)
            # print(cpu_percent)
            # print(memory)
            # TODO: insert in database

    def stop(self, duration):
        self._stopped = True
