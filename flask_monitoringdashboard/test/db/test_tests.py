"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/tests.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, mean, \
    EXECUTION_TIMES, NAME

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
                add_test_result(db_session, NAME, exec_time, datetime.datetime.utcnow(), config.version, SUITE, 2)
            result = get_test_cnt_avg(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, NAME)
            self.assertEqual(result[0].count, len(EXECUTION_TIMES))
            self.assertEqual(result[0].average, mean(EXECUTION_TIMES))

    def test_get_suite_nr(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_next_suite_nr, add_test_result
        from flask_monitoringdashboard import config
        import datetime
        with session_scope() as db_session:
            self.assertEqual(get_next_suite_nr(db_session), 1)
            add_test_result(db_session, NAME, 1234, datetime.datetime.utcnow(), config.version, SUITE, 2)
            self.assertEqual(get_next_suite_nr(db_session), SUITE + 1)

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
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            self.assertEqual(get_suite_measurements(db_session, SUITE), [])
            self.test_add_test_result()
            result = get_suite_measurements(db_session, SUITE)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for test_run in result:
                self.assertEqual(test_run.name, NAME)
                self.assertIn(test_run.execution_time, EXECUTION_TIMES)
                self.assertEqual(test_run.version, config.version)
                self.assertEqual(test_run.suite, SUITE)

    def test_get_test_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_test_measurements
        from flask_monitoringdashboard import config
        with session_scope() as db_session:
            self.assertEqual(get_test_measurements(db_session, NAME, SUITE), [])
            self.test_add_test_result()
            result = get_test_measurements(db_session, NAME, SUITE)
            self.assertEqual(len(result), len(EXECUTION_TIMES))
            for test_run in result:
                self.assertEqual(test_run.name, NAME)
                self.assertIn(test_run.execution_time, EXECUTION_TIMES)
                self.assertEqual(test_run.version, config.version)
                self.assertEqual(test_run.suite, SUITE)
