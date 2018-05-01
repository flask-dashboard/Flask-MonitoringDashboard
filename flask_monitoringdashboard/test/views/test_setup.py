import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, login, \
    NAME, test_admin_secure


class TestSetup(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_configuration(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'configuration')

    def test_rules(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'rules')

    def test_test_result(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'testmonitor/{}'.format(NAME))

    def test_testmonitor(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'testmonitor')

    def test_monitor_rule(self):
        """
            Test whether it is possible to monitor a rule
        """
        data = {'checkbox-static': True}
        with self.app.test_client() as c:
            login(c)
            self.assertEqual(200, c.post('dashboard/rules', data=data).status_code)
