"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/function_calls.py')
    See __init__.py for how to run the test-cases.
"""

import time
import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, EXECUTION_TIMES, TIMES, \
    NAME, GROUP_BY, IP


class TestFunctionCall(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_function_call(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import add_function_call, get_data_per_endpoint
        name2 = 'main2'
        execution_time = 1234
        self.assertNotEqual(NAME, name2, 'Both cannot be equal, otherwise the test will fail')
        with session_scope() as db_session:
            self.assertEqual(len(get_data_per_endpoint(db_session, name2)), 0)
            add_function_call(db_session, execution_time, name2, ip=IP)

            result2 = get_data_per_endpoint(db_session, name2)
            self.assertEqual(len(result2), 1)
            self.assertEqual(result2[0].endpoint, name2)
            self.assertEqual(result2[0].execution_time, execution_time)

    def test_get_data_from(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import get_data_between
        size = 2
        first = len(TIMES) - size - 1
        with session_scope() as db_session:
            result = get_data_between(db_session, TIMES[-size - 2], TIMES[-1])
            for i in range(size):
                self.assertEqual(result[i].endpoint, NAME)
                self.assertEqual(result[i].execution_time, EXECUTION_TIMES[first + i])
                self.assertEqual(result[i].time, TIMES[first + i])
                self.assertEqual(result[i].group_by, GROUP_BY)
                self.assertEqual(result[i].ip, IP)

    def test_get_data(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import get_data, config
        with session_scope() as db_session:
            result = get_data(db_session)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for i in range(len(EXECUTION_TIMES)):
                self.assertEqual(result[i].endpoint, NAME)
                self.assertEqual(result[i].execution_time, EXECUTION_TIMES[i])
                self.assertEqual(result[i].time, TIMES[i])
                self.assertEqual(result[i].group_by, GROUP_BY)
                self.assertEqual(result[i].version, config.version)
                self.assertEqual(result[i].ip, IP)

    def test_get_data_per_version(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import get_data_per_version, config
        new_version = 1.1
        self.assertNotEqual(config.version, new_version)
        with session_scope() as db_session:
            self.assertEqual(get_data_per_version(db_session, new_version), [])

            result = get_data_per_version(db_session, config.version)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for i in range(len(EXECUTION_TIMES)):
                self.assertEqual(result[i].execution_time, EXECUTION_TIMES[i])
                self.assertEqual(result[i].version, config.version)

    def test_get_versions(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import config
        from flask_monitoringdashboard.database.versions import get_versions
        with session_scope() as db_session:
            result = get_versions(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], config.version)

    def test_get_data_per_endpoint(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import get_data_per_endpoint
        new_name = 'main2'
        with session_scope() as db_session:
            self.assertNotEqual(NAME, new_name)
            self.assertEqual(get_data_per_endpoint(db_session, new_name), [])

            result = get_data_per_endpoint(db_session, NAME)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for i in range(len(EXECUTION_TIMES)):
                self.assertEqual(result[i].endpoint, NAME)
                self.assertEqual(result[i].execution_time, EXECUTION_TIMES[i])

    def test_get_endpoints(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import get_endpoints
        with session_scope() as db_session:
            result = get_endpoints(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], NAME)

    def test_get_date_of_first_request(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.function_calls import get_date_of_first_request
        with session_scope() as db_session:
            self.assertEqual(get_date_of_first_request(db_session), int(time.mktime(TIMES[0].timetuple())))
