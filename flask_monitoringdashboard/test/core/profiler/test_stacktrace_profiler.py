import threading
import unittest

from flask_monitoringdashboard.core.profiler import StacktraceProfiler
from flask_monitoringdashboard.database import Endpoint
from flask_monitoringdashboard.test.utils import NAME, set_test_environment, clear_db, add_fake_data, get_test_app


class TestStacktraceProfiler(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_after_run(self):
        with self.app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            current_thread = threading.current_thread().ident
            ip = request.environ['REMOTE_ADDR']
            thread = StacktraceProfiler(current_thread, Endpoint(id=0, name=NAME), ip)
            thread._keeprunning = False
            self.assertRaises(ValueError, thread.run)
