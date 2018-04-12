import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, login, get_test_app


class TestLogin(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_login(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(200, self.app.get('dashboard/login').status_code)
        login(self.app)
        self.assertEqual(302, self.app.get('dashboard/login').status_code)
