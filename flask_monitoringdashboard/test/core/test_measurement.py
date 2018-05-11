import unittest

from flask import Flask

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times, get_monitor_rule
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data

NAME = 'func'


class TestMeasurement(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = Flask(__name__)

    @staticmethod
    def func():
        """ function for testing the performance """
        return 'Hello World!'

    def test_get_group_by(self):
        """
            Test whether the group_by returns the right result
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.core.group_by import get_group_by
        config.group_by = lambda: 3
        self.assertEqual(get_group_by(), '3')

        config.group_by = (lambda: 'User', lambda: 3.0)
        self.assertEqual(get_group_by(), '(User,3.0)')

    def test_track_performance(self):
        """
            Test whether the track_performance works
        """
        from flask_monitoringdashboard.core.measurement import track_performance

        with self.app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            self.func = track_performance(self.func, NAME)
            self.func()
            with session_scope() as db_session:
                self.assertEqual(count_requests(db_session, NAME), 1)

    def test_last_accessed(self):
        """
            Test whether the last_accessed is stored in the database
        """
        from flask_monitoringdashboard.core.measurement import track_last_accessed
        from flask_monitoringdashboard.database.count_group import get_value

        with session_scope() as db_session:
            get_monitor_rule(db_session, NAME)
            func = track_last_accessed(self.func, NAME)

        with session_scope() as db_session:
            self.assertIsNone(get_value(get_last_accessed_times(db_session), NAME, default=None))
            func()
            self.assertIsNotNone(get_value(get_last_accessed_times(db_session), NAME, default=None))

    def test_get_average(self):
        """
            Test get_average
        """
        from flask_monitoringdashboard.core.measurement import track_performance, get_average, MIN_NUM_REQUESTS
        self.assertIsNone(get_average(NAME))

        with self.app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            self.func = track_performance(self.func, NAME)
            for i in range(MIN_NUM_REQUESTS):
                self.func()

        self.assertIsNotNone(get_average(NAME))
