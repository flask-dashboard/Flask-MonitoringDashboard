"""
    This file contains all unit tests that count a number of results in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/count.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_versions_endpoint
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, ENDPOINT_ID


class TestCount(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_count_versions(self):
        with session_scope() as db_session:
            self.assertEqual(count_versions_endpoint(db_session, ENDPOINT_ID), 1)
