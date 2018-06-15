"""
    This file contains all unit tests that count a number of results in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/count.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope, Endpoint
from flask_monitoringdashboard.database.count import count_versions_endpoint, count_rows, count_users, count_ip, \
    count_versions, count_test_builds, count_builds_endpoint, count_requests, count_total_requests, count_outliers, \
    count_profiled_requests
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, ENDPOINT_ID, REQUESTS, \
    OUTLIER_COUNT


class TestCount(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_count_rows(self):
        with session_scope() as db_session:
            self.assertEqual(count_rows(db_session, Endpoint.id), 1)
            self.assertEqual(count_rows(db_session, Endpoint.id, Endpoint.id == ENDPOINT_ID+1), 0)

    def test_count_users(self):
        with session_scope() as db_session:
            self.assertEqual(count_users(db_session, ENDPOINT_ID), 1)
            self.assertEqual(count_users(db_session, ENDPOINT_ID+1), 0)

    def test_count_ip(self):
        with session_scope() as db_session:
            self.assertEqual(count_ip(db_session, ENDPOINT_ID), 1)
            self.assertEqual(count_ip(db_session, ENDPOINT_ID+1), 0)

    def test_count_versions(self):
        with session_scope() as db_session:
            self.assertEqual(count_versions(db_session), 1)

    def test_count_test_builds(self):
        with session_scope() as db_session:
            self.assertEqual(count_test_builds(db_session), 0)

    def test_count_builds_endpoint(self):
        with session_scope() as db_session:
            self.assertEqual(count_builds_endpoint(db_session), 0)

    def test_count_versions_endpoint(self):
        with session_scope() as db_session:
            self.assertEqual(count_versions_endpoint(db_session, ENDPOINT_ID), 1)
            self.assertEqual(count_versions_endpoint(db_session, ENDPOINT_ID+1), 0)

    def test_count_requests(self):
        with session_scope() as db_session:
            self.assertEqual(count_requests(db_session, ENDPOINT_ID), len(REQUESTS))
            self.assertEqual(count_requests(db_session, ENDPOINT_ID + 1), 0)

    def test_count_total_requests(self):
        with session_scope() as db_session:
            self.assertEqual(count_total_requests(db_session), len(REQUESTS))

    def test_count_outliers(self):
        with session_scope() as db_session:
            self.assertEqual(count_outliers(db_session, ENDPOINT_ID), OUTLIER_COUNT)
            self.assertEqual(count_outliers(db_session, ENDPOINT_ID+1), 0)

    def test_count_profiled_requests(self):
        with session_scope() as db_session:
            self.assertEqual(count_profiled_requests(db_session, ENDPOINT_ID), 0)