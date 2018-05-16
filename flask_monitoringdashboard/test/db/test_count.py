"""
    This file contains all unit tests that count a number of results in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/count.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_versions_end
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME


class TestCount(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_count_versions(self):
        with session_scope() as db_session:
            self.assertEqual(count_versions_end(db_session, NAME), 1)
