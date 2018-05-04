"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/outlier.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME, OUTLIER_COUNT


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
            self.assertEqual(len(db_session.query(Outlier).all()), OUTLIER_COUNT)
        # TODO: Complete function

    def test_get_outliers(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import get_outliers_sorted, Outlier
        with session_scope() as db_session:
            outliers = get_outliers_sorted(db_session, NAME, Outlier.time, offset=0, per_page=10)
        self.assertEqual(len(outliers), OUTLIER_COUNT)
        for i, outlier in enumerate(outliers):
            self.assertEqual(outlier.endpoint, NAME)
            if i == 0:
                continue
            self.assertTrue(outlier.time <= outliers[i - 1].time)

    def test_count_outliers(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.count import count_outliers
        with session_scope() as db_session:
            self.assertEqual(count_outliers(db_session, NAME), OUTLIER_COUNT)

    def test_get_outliers_cpus(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import get_outliers_cpus
        expected_cpus = []
        for i in range(OUTLIER_COUNT):
            expected_cpus.append(('[%d, %d, %d, %d]' % (i, i + 1, i + 2, i + 3),))
        with session_scope() as db_session:
            self.assertEqual(get_outliers_cpus(db_session, NAME), expected_cpus)

    def test_get_mean_cpu(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import get_outliers_cpus
        from flask_monitoringdashboard.core.utils import get_mean_cpu
        with session_scope() as db_session:
            all_cpus = get_outliers_cpus(db_session, NAME)
        expected_mean = []
        self.assertTrue(True)
        for i in range(4):
            expected_mean.append((OUTLIER_COUNT - 1) / 2 + i)
        self.assertEqual(get_mean_cpu(all_cpus), expected_mean)
