import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, \
    test_admin_secure, NAME


class TestTestMonitor(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_build_performance(self):
        test_admin_secure(self, 'test_build_performance')

    def test_endpoint_build_performance(self):
        test_admin_secure(self, 'endpoint_build_performance')

    def test_testmonitor(self):
        test_admin_secure(self, 'testmonitor')

    def test_endpoint_test_details(self):
        test_admin_secure(self, 'testmonitor/{}'.format(NAME))
