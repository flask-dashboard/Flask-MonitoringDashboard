"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/endpoint.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.core.timezone import to_utc_datetime
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME
import pytz


class TestEndpoint(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_get_monitor_rule(self):
        """
            Test wheter the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_monitor_rule
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            rule = get_monitor_rule(db_session, NAME)
        self.assertEqual(rule.endpoint, NAME)
        self.assertTrue(rule.monitor)
        self.assertEqual(rule.version_added, config.version)

    def test_update_monitor_rule(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_monitor_rule, update_monitor_rule
        with session_scope() as db_session:
            current_value = get_monitor_rule(db_session, NAME).monitor
            new_value = not current_value
            update_monitor_rule(db_session, NAME, new_value)
            self.assertEqual(get_monitor_rule(db_session, NAME).monitor, new_value)

    def test_update_last_accessed(self):
        """
            Test whether the function returns the right values.
        """
        import datetime
        time = datetime.datetime.utcnow()
        from flask_monitoringdashboard.database.endpoint import update_last_accessed, get_last_accessed_times
        from flask_monitoringdashboard.database.count_group import get_value
        with session_scope() as db_session:
            update_last_accessed(db_session, NAME, time)
            result = get_value(get_last_accessed_times(db_session), NAME)
            result_utc = to_utc_datetime(result)
            self.assertEqual(result_utc, time)
