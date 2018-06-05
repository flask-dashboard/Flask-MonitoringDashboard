"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/endpoint.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.core.timezone import to_utc_datetime
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME, TIMES
import pytz


class TestEndpoint(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_get_endpoint(self):
        """
            Test wheter the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            endpoint = get_endpoint_by_name(db_session, NAME)
        self.assertEqual(endpoint.name, NAME)
        self.assertEqual(endpoint.monitor_level, 1)
        self.assertEqual(endpoint.version_added, config.version)

    def test_update_endpoint(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name, update_endpoint
        with session_scope() as db_session:
            current_value = get_endpoint_by_name(db_session, NAME).monitor_level
            new_value = 1 if current_value != 1 else 2
            update_endpoint(db_session, NAME, new_value)
            self.assertEqual(get_endpoint_by_name(db_session, NAME).monitor_level, new_value)

    def test_update_last_accessed(self):
        """
            Test whether the function returns the right values.
        """
        import datetime
        time = datetime.datetime.utcnow()
        from flask_monitoringdashboard.database.endpoint import update_last_accessed, get_last_requested
        from flask_monitoringdashboard.database.count_group import get_value
        with session_scope() as db_session:
            update_last_accessed(db_session, NAME)
            result = get_value(get_last_requested(db_session), NAME)
            result_utc = to_utc_datetime(result)
            self.assertTrue((result_utc - time).seconds < 1)

    def test_endpoints(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoint_data
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            result = get_endpoint_data(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, NAME)
            self.assertEqual(result[0].monitor_level, 1)
            self.assertEqual(result[0].version_added, config.version)
            self.assertEqual(result[0].last_requested, TIMES[0])

    def test_get_monitor_data(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoints, get_endpoint_data
        # since all monitor-rules in the test-database have the 'monitor'-variable set to True, the outcome of both
        # functions is equivalent
        with session_scope() as db_session:
            result1 = get_endpoint_data(db_session)
            result2 = get_endpoints(db_session)
            self.assertEqual(len(result1), len(result2))
            self.assertEqual(result1[0].name, result2[0].name)
            self.assertEqual(result1[0].last_requested, result2[0].last_requested)
            self.assertEqual(result1[0].monitor_level, result2[0].monitor_level)
            self.assertEqual(result1[0].time_added, result2[0].time_added)
            self.assertEqual(result1[0].version_added, result2[0].version_added)
