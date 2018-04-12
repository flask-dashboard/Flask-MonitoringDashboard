import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, login, \
    NAME


class TestSetup(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_settings(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/settings').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/settings').status_code)

    def test_rules(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/rules').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/rules').status_code)

    def test_test_result(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/testmonitor/{}'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/testmonitor/{}'.format(NAME)).status_code)

    def test_testmonitor(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/testmonitor').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/testmonitor').status_code)
