"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/tests.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, mean, \
    EXECUTION_TIMES, NAME, TEST_NAMES

NAME2 = 'main2'
SUITE = 3


class TestDBTests(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_test_result(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_test_cnt_avg, add_test_result
        from flask_monitoringdashboard import config
        import datetime
        with session_scope() as db_session:
            self.assertEqual(get_test_cnt_avg(db_session), [])
            for exec_time in EXECUTION_TIMES:
                for test in TEST_NAMES:
                    add_test_result(db_session, test, exec_time, datetime.datetime.utcnow(), config.version, SUITE, 0)
            result = get_test_cnt_avg(db_session)
            self.assertEqual(2, len(result))
            self.assertEqual(TEST_NAMES[0], result[0].name)
            self.assertEqual(len(EXECUTION_TIMES), result[0].count)
            self.assertEqual(mean(EXECUTION_TIMES), result[0].average)

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
            self.assertEqual(get_test_suites(db_session), [(SUITE,)])

    def test_get_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_suite_measurements
        with session_scope() as db_session:
            self.assertEqual(get_suite_measurements(db_session, SUITE), [0])
            self.test_add_test_result()
            result = get_suite_measurements(db_session, SUITE)
            self.assertEqual(len(EXECUTION_TIMES) * 2, len(result))

    def test_get_test_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_test_measurements
        with session_scope() as db_session:
            self.assertEqual(get_test_measurements(db_session, NAME, SUITE), [0])
            self.test_add_test_result()
            result = get_test_measurements(db_session, NAME, SUITE)
            self.assertEqual(len(EXECUTION_TIMES) * 2, len(result))
