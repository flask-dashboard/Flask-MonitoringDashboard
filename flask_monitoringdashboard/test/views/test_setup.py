import os
import subprocess
import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, add_fake_test_runs, \
    get_test_app, login, NAME, test_admin_secure, test_get_ok, test_get_redirect


class TestSetup(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_index(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_get_redirect(self, '')

    def test_static(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_get_ok(self, 'static/css/custom.css')

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
        add_fake_test_runs()
        test_admin_secure(self, 'testmonitor/{}'.format(NAME))

    def test_testmonitor(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        add_fake_test_runs()
        test_admin_secure(self, 'testmonitor')

    def test_monitor_rule(self):
        """
            Test whether it is possible to monitor a rule
        """
        data = {'checkbox-static': True}
        with self.app.test_client() as c:
            login(c)
            self.assertEqual(200, c.post('dashboard/rules', data=data).status_code)

    def test_collect_performance(self):
        """
            Tests the collect_performance script.
        """
        test_dir = os.getcwd() + '/flask_monitoringdashboard/test/db'  # Finds the database tests of the Dashboard.
        self.assertEqual(0, subprocess.call(
            'python -m flask_monitoringdashboard.collect_performance --test_folder={} --times=1'.format(test_dir),
            shell=True))
