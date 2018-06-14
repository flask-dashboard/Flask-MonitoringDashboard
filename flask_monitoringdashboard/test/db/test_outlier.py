"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/outlier.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.outlier import add_outlier
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME, OUTLIER_COUNT, \
    ENDPOINT_ID


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
            request = "headers", "environ", "url"
            add_outlier(db_session, request_id=1, cpu_percent="cpu_percent", memory="memory",
                        stacktrace="stacktrace", request=request)
            self.assertEqual(len(db_session.query(Outlier).all()), OUTLIER_COUNT+1)

    def test_get_outliers(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import get_outliers_sorted
        with session_scope() as db_session:
            outliers = get_outliers_sorted(db_session, endpoint_id=ENDPOINT_ID, offset=0, per_page=10)
        self.assertEqual(len(outliers), OUTLIER_COUNT)
        for i, outlier in enumerate(outliers):
            self.assertEqual(outlier.request.endpoint.name, NAME)
            if i == 0:
                continue
            self.assertTrue(outlier.request.time_requested <= outliers[i - 1].request.time_requested)

    def test_count_outliers(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.count import count_outliers
        with session_scope() as db_session:
            self.assertEqual(count_outliers(db_session, ENDPOINT_ID), OUTLIER_COUNT)

    def test_get_outliers_cpus(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.outlier import get_outliers_cpus
        expected_cpus = []
        for i in range(OUTLIER_COUNT):
            expected_cpus.append('[%d, %d, %d, %d]' % (i, i + 1, i + 2, i + 3))
        with session_scope() as db_session:
            self.assertEqual(get_outliers_cpus(db_session, ENDPOINT_ID), expected_cpus)
