"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'dashboard/database/monitor-rules.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, TEST_NAMES

NAME2 = 'main2'
SUITE = 3


class TestDBTestsGrouped(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_reset_tests_grouped(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests_grouped import reset_tests_grouped, get_tests_grouped
        self.assertEqual(len(get_tests_grouped()), len(TEST_NAMES))
        reset_tests_grouped()
        self.assertEqual(get_tests_grouped(), [])

    def test_add_tests_grouped(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests_grouped import add_tests_grouped, get_tests_grouped
        json = [{'endpoint': 'endpoint', 'test_name': 'test_name'}]
        self.assertEqual(len(get_tests_grouped()), len(TEST_NAMES))
        add_tests_grouped(json)
        self.assertEqual(len(get_tests_grouped()), len(TEST_NAMES)+1)

    def test_get_tests_grouped(self):
        """
            Test whether the function returns the right values.
        """
        self.test_reset_tests_grouped()  # can be replaced by test_add_test_result, since this function covers two tests
