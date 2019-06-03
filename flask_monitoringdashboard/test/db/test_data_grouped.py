import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.data_grouped import get_endpoint_data_grouped, \
    get_version_data_grouped, get_host_data_grouped
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, REQUESTS


class TestDataGrouped(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    @staticmethod
    def median(values):
        return sum(values) / len(values)

    def test_get_endpoint_data_grouped(self):
        with session_scope() as db_session:
            self.assertEqual(get_endpoint_data_grouped(db_session, self.median), {1: 12000}.items())

    def test_get_version_data_grouped(self):
        with session_scope() as db_session:
            self.assertEqual(get_version_data_grouped(db_session, lambda x: x), {'1.0': REQUESTS}.items())

    def test_get_host_data_grouped(self):
        with session_scope() as db_session:
            d = {1: [1000.0, 3000.0, 50000.0], 2: [2000.0, 4000.0]}
            r = dict(get_host_data_grouped(db_session, lambda x: x))
            self.assertEqual(r[1], d[1])
            self.assertEqual(r[2], d[2])
