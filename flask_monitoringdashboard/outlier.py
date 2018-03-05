"""
    Create a StackInfo-object and it will spawn a different thread.
    That thread will sleep for 'average' ms (reformatted to seconds).
    Then it will log the stacktrace of all active threads.
    Moreover, it logs cpu- and memory-info.
"""

import time
import traceback
from threading import Thread, enumerate
import sys
import psutil


class StackInfo(object):
    def __init__(self, average):
        self.average = average
        self.stacktrace = ''
        self.cpu_percent = ''
        self.memory = ''

        try:
            thread = Thread(target=log_stack_trace, args=(self,))
            thread.start()
        except Exception:
            print('Can\'t log traceback information')
            traceback.print_exc()


def log_stack_trace(stack_info):
    # average is in ms, sleep requires seconds
    time.sleep(stack_info.average / 1000.0)

    # iterate through every active thread and get the stack-trace
    stack_list = []
    try:
        for th in enumerate():
            try:
                f = open('stacktrace.log', 'w+')
                stack_list.extend(['', str(th)])
                traceback.print_stack(sys._current_frames()[th.ident], file=f)
                f.close()
                f = open('stacktrace.log', 'r')
                stack_list.extend(f.readlines())
            except Exception as e:
                print('Exception occurred: {}'.format(e))
                traceback.print_exc()
    except Exception as e:
        print('Exception occurred: {}'.format(e))
        traceback.print_exc()

    # Set the values in the object
    stack_info.stacktrace = '<br />'.join(stack_list)
    stack_info.cpu_percent = str(psutil.cpu_percent(interval=None, percpu=True))
    stack_info.memory = str(psutil.virtual_memory())
