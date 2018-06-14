import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.tested_endpoints import get_tested_endpoint_names
from flask_monitoringdashboard.test.db.test_count_group import TestCountGroup
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME


class TestTestedEndpoints(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_get_tested_endpoint_names(self):
        with session_scope() as db_session:
            TestCountGroup.add_test_data(db_session)
            self.assertEqual(get_tested_endpoint_names(db_session), [NAME])
