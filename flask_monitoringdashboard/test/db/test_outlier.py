"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'dashboard/database/monitor-rules.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME


class TestMonitorRule(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_outlier(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import Outlier
        with session_scope() as db_session:
            self.assertEqual(db_session.query(Outlier).all(), [])
        # TODO: Complete function

    def test_get_outliers(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import get_outliers_sorted, Outlier
        with session_scope() as db_session:
            self.assertEqual(get_outliers_sorted(db_session, NAME, Outlier.time, offset=0, per_page=10), [])

    def test_count_outliers(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.count import count_outliers
        with session_scope() as db_session:
            self.assertEqual(count_outliers(db_session, NAME), 0)
