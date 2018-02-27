"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the file:
    'dashboard/database/endpoint.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, mean, \
    EXECUTION_TIMES, TIMES, NAME, GROUP_BY, IP


class TestEndpoint(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_get_line_results(self):
        """
            Test whether the function returns the right values.
            It should return the average, min and max and length (count).
        """
        from flask_monitoringdashboard.database.endpoint import get_line_results
        result = get_line_results(NAME)[0]
        self.assertEqual(result.avg, mean(EXECUTION_TIMES))
        self.assertEqual(result.min, min(EXECUTION_TIMES))
        self.assertEqual(result.max, max(EXECUTION_TIMES))
        self.assertEqual(result.count, len(EXECUTION_TIMES))

    def test_get_num_requests(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_num_requests
        result = get_num_requests(NAME)[0]
        self.assertEqual(result.count, len(EXECUTION_TIMES))

    def test_get_endpoint_column(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoint_column
        from flask_monitoringdashboard.database import FunctionCall
        result = get_endpoint_column(NAME, FunctionCall.time)
        self.assertEqual(len(result), len(EXECUTION_TIMES))
        self.assertEqual(result[0].time, TIMES[0])

    def test_get_endpoint_column_user_sorted(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoint_column_user_sorted
        from flask_monitoringdashboard.database import FunctionCall
        result = get_endpoint_column_user_sorted(NAME, FunctionCall.time)
        self.assertEqual(len(result), len(EXECUTION_TIMES))
        self.assertEqual(result[0].time, TIMES[0])

    def test_get_endpoint_results(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoint_results
        from flask_monitoringdashboard.database import FunctionCall
        result = get_endpoint_results(NAME, FunctionCall.group_by)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].average, mean(EXECUTION_TIMES))
        self.assertEqual(result[0].count, len(EXECUTION_TIMES))

    def test_get_monitor_rule(self):
        """
            Test wheter the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_monitor_rule
        from flask_monitoringdashboard import config
        rule = get_monitor_rule(NAME)
        self.assertEqual(rule.endpoint, NAME)
        self.assertTrue(rule.monitor)
        self.assertEqual(rule.version_added, config.version)

    def test_update_monitor_rule(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_monitor_rule, update_monitor_rule
        current_value = get_monitor_rule(NAME).monitor
        new_value = not current_value
        update_monitor_rule(NAME, new_value)
        self.assertEqual(get_monitor_rule(NAME).monitor, new_value)

    def test_get_all_measurement(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.database.endpoint import get_all_measurement
        result = get_all_measurement(NAME)
        self.assertEqual(len(result), len(EXECUTION_TIMES))
        for row in result:
            self.assertIn(row.execution_time, EXECUTION_TIMES)
            self.assertEqual(row.version, config.version)
            self.assertEqual(row.endpoint, NAME)
            self.assertEqual(row.group_by, GROUP_BY)
            self.assertEqual(row.ip, IP)

    def test_get_all_measurement_per_column(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column
        from flask_monitoringdashboard.database import FunctionCall
        from flask_monitoringdashboard import config
        result = get_all_measurement_per_column(endpoint=NAME, column=FunctionCall.ip, value=IP)
        self.assertEqual(len(result), len(EXECUTION_TIMES))
        for row in result:
            self.assertIn(row.execution_time, EXECUTION_TIMES)
            self.assertEqual(row.version, config.version)
            self.assertEqual(row.endpoint, NAME)
            self.assertEqual(row.group_by, GROUP_BY)
            self.assertEqual(row.ip, IP)

    def test_get_last_accessed_times(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_last_accessed_times
        result = get_last_accessed_times()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].endpoint, NAME)

    def test_update_last_accessed(self):
        """
            Test whether the function returns the right values.
        """
        import datetime
        time = datetime.datetime.now()
        from flask_monitoringdashboard.database.endpoint import update_last_accessed, get_last_accessed_times
        update_last_accessed(NAME, time)
        result = get_last_accessed_times()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].endpoint, NAME)
        self.assertEqual(result[0].last_accessed, time)
