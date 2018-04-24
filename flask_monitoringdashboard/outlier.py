"""
    Create a StackInfo-object and it will spawn a different thread.
    That thread will sleep for 'average' ms (reformatted to seconds).
    Then it will log the stacktrace of all active threads.
    Moreover, it logs cpu- and memory-info.
"""

import time
import traceback
from threading import Thread
import sys
import psutil


class StackInfo(object):
    def __init__(self, average):
        self.average = average
        self.stacktrace = ''
        self.cpu_percent = ''
        self.memory = ''
        self.stopped = False

        try:
            thread = Thread(target=self.log_stack_trace)
            thread.start()
        except Exception as e:
            print('Can\'t log traceback information: {}'.format(e))
            traceback.print_exc()

    def stop(self):
        self.stopped = True

    def log_stack_trace(self):
        # average is in ms, sleep requires seconds
        time.sleep(self.average / 1000.0)

        if self.stopped:
            return

            # iterate through every active thread and store the stack-trace
        stack_list = []
        for thread_id, stack in sys._current_frames().items():
            stack_list.append("\n# Thread_id: %s" % thread_id)
            for filename, lineno, name, line in traceback.extract_stack(stack):
                stack_list.append('File: "%s", line %d, in %s' % (filename, lineno, name))
                if line:
                    stack_list.append("  %s" % (line.strip()))

        # Set the values in the object
        self.stacktrace = '<br />'.join(stack_list)
        self.cpu_percent = str(psutil.cpu_percent(interval=None, percpu=True))
        self.memory = str(psutil.virtual_memory())
