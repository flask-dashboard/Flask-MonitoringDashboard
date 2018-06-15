import unittest

from flask_monitoringdashboard.test.utils import get_test_app


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = get_test_app()

    def test_check_login(self):
        """
            Test if function 'check_login' works
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.core.auth import check_login

        with self.app.test_request_context():
            self.assertTrue(check_login(config.username, config.password))
            self.assertTrue(check_login(config.guest_username, config.guest_password[0]))
