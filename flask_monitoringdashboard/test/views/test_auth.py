import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, login, get_test_app


class TestLogin(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_get_login(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(200, self.app.get('dashboard/login').status_code)
        login(self.app)
        self.assertEqual(302, self.app.get('dashboard/login').status_code)

    def test_incorrect_login(self):
        """
            Try whether logging with incorrect credentials returns the login page
        """
        args = {'name': 'admin', 'password': 'wrong'}
        self.assertIn('formLogin', self.app.post('dashboard/login', data=args).data.decode())

    def test_correct_login(self):
        """
            Try whether logging with correct credentials does not return the login page
        """
        args = {'name': 'admin', 'password': 'admin'}
        self.assertNotIn('formLogin', self.app.post('dashboard/login', data=args).data.decode())

    def test_logout(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/logout').status_code)
