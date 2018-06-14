"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/tests.py')
    See info_box.py for how to run the test-cases.
"""

import unittest
import datetime

from flask_monitoringdashboard.database import session_scope, TestEndpoint
from flask_monitoringdashboard.database.tests import get_endpoint_measurements, get_last_tested_times
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, add_fake_test_runs, \
    REQUESTS, NAME, TEST_NAMES, ENDPOINT_ID

NAME2 = 'main2'
SUITE = 3


class TestDBTests(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        add_fake_test_runs()

    def test_add_test_result(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import add_test_result, get_suite_measurements, add_or_update_test
        from flask_monitoringdashboard.database.tested_endpoints import add_endpoint_hit
        from flask_monitoringdashboard import config
        import datetime
        with session_scope() as db_session:
            self.assertEqual(get_suite_measurements(db_session, SUITE), [0])
            for exec_time in REQUESTS:
                for test in TEST_NAMES:
                    add_or_update_test(db_session, test, True, datetime.datetime.utcnow(), config.version)
                    add_test_result(db_session, test, exec_time, datetime.datetime.utcnow(), config.version, SUITE, 0)
                    add_endpoint_hit(db_session, NAME, exec_time, test, config.version, SUITE)
            result = get_suite_measurements(db_session, SUITE)
            self.assertEqual(len(result), len(REQUESTS) * len(TEST_NAMES))

    def test_get_results(self):
        """
            Test whether the function returns the right values.
        """
        self.test_add_test_result()  # can be replaced by test_add_test_result, since this function covers two tests

    def test_get_suites(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_test_suites
        self.test_add_test_result()
        with session_scope() as db_session:
            self.assertEqual(2, len(get_test_suites(db_session)))

    def test_get_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_suite_measurements
        with session_scope() as db_session:
            self.assertEqual(get_suite_measurements(db_session, SUITE), [0])
            self.test_add_test_result()
            result = get_suite_measurements(db_session, SUITE)
            self.assertEqual(len(REQUESTS) * 2, len(result))

    def test_get_test_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_endpoint_measurements_job
        with session_scope() as db_session:
            self.assertEqual(1, len(get_endpoint_measurements_job(db_session, NAME, SUITE)))
            self.test_add_test_result()
            result = get_endpoint_measurements_job(db_session, NAME, SUITE)
            self.assertEqual(len(TEST_NAMES) * len(REQUESTS), len(result))

    def test_get_endpoint_measurements(self):
        with session_scope() as db_session:
            self.assertEqual(get_endpoint_measurements(db_session, "1"), [0])
            db_session.add(TestEndpoint(endpoint_id=ENDPOINT_ID, test_id=1, duration=1234, app_version="1.0",
                                        travis_job_id="1", time_added=datetime.datetime.utcnow()))
            db_session.add(TestEndpoint(endpoint_id=ENDPOINT_ID, test_id=1, duration=2345, app_version="1.0",
                                        travis_job_id="1", time_added=datetime.datetime.utcnow()))
            self.assertEqual(get_endpoint_measurements(db_session, "1"), [1234, 2345])

    def test_get_last_tested_times(self):
        with session_scope() as db_session:
            self.assertEqual(get_last_tested_times(db_session), [])
            db_session.add(TestEndpoint(endpoint_id=ENDPOINT_ID, test_id=1, duration=1234, app_version="1.0",
                                        travis_job_id="1", time_added=datetime.datetime.utcnow()))
            self.assertNotEqual(get_last_tested_times(db_session), [])
