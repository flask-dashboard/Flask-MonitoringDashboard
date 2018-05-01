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
        with self.app.test_client() as c:
            self.assertEqual(200, c.get('dashboard/login').status_code)
            login(c)
            self.assertEqual(302, c.get('dashboard/login').status_code)

    def test_incorrect_login(self):
        """
            Try whether logging with incorrect credentials returns the login page
        """
        args = {'name': 'admin', 'password': 'wrong'}
        with self.app.test_client() as c:
            self.assertIn('formLogin', c.post('dashboard/login', data=args).data.decode())

    def test_correct_login(self):
        """
            Try whether logging with correct credentials does not return the login page
        """
        args = {'name': 'admin', 'password': 'admin'}
        with self.app.test_client() as c:
            self.assertNotIn('formLogin', c.post('dashboard/login', data=args).data.decode())

    def test_logout(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        with self.app.test_client() as c:
            self.assertEqual(302, c.get('dashboard/logout').status_code)
