import threading
import time
import unittest

from flask_monitoringdashboard.core.profiler import start_thread_last_requested, start_performance_thread, \
    start_profiler_thread, start_profiler_and_outlier_thread
from flask_monitoringdashboard.database import Endpoint
from flask_monitoringdashboard.test.utils import NAME, set_test_environment, clear_db, add_fake_data, get_test_app


class TestProfiler(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    @staticmethod
    def wait_until_threads_finished(num_threads):
        while threading.active_count() > num_threads:
            time.sleep(0.001)

    def test_start_thread_last_requested(self):
        num_threads = threading.active_count()
        start_thread_last_requested(Endpoint(id=1, name=NAME))
        self.assertEqual(threading.active_count(), num_threads + 1)
        self.wait_until_threads_finished(num_threads)

    def test_start_performance_thread(self):
        with self.app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            num_threads = threading.active_count()
            start_performance_thread(Endpoint(id=1, name=NAME), 1234)
            self.assertEqual(threading.active_count(), num_threads + 1)
            self.wait_until_threads_finished(num_threads)

    def test_start_profiler_thread(self):
        with self.app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            num_threads = threading.active_count()
            thread = start_profiler_thread(Endpoint(id=1, name=NAME))
            self.assertEqual(threading.active_count(), num_threads + 1)
            thread.stop(1)
            self.wait_until_threads_finished(num_threads)

    def test_start_profiler_and_outlier_thread(self):
        with self.app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            num_threads = threading.active_count()
            thread = start_profiler_and_outlier_thread(Endpoint(id=1, name=NAME))
            self.assertEqual(threading.active_count(), num_threads + 2)
            thread.stop(1)
            self.wait_until_threads_finished(num_threads)
