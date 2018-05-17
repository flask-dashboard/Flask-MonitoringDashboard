import datetime
import unittest

import jwt
from flask import json

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, \
    EXECUTION_TIMES, NAME, GROUP_BY, IP, TIMES, test_admin_secure, test_post_data


class TestExportData(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_download_csv(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'download-csv')

    def test_export_data(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'view-csv')

    def test_submit_test_results(self):
        """
            Submit some collect_performance data.
        """
        test_results = {'test_runs': [], 'grouped_tests': []}
        test_results['test_runs'].append(
            {'name': 'test_1', 'exec_time': 50, 'time': str(datetime.datetime.now()), 'successful': True, 'iter': 1})
        test_results['grouped_tests'].append({'endpoint': 'endpoint_1', 'test_name': 'test_1'})
        test_results['app_version'] = '1.0'
        test_results['travis_job'] = '133.7'
        test_post_data(self, 'submit-test-results', test_results)

    def test_get_json_data_from(self):
        """
            Test whether the response is as it should be.
        """
        from flask_monitoringdashboard import config
        with self.app.test_client() as c:
            result = c.get('dashboard/get_json_data').data
        decoded = jwt.decode(result, config.security_token, algorithms=['HS256'])
        data = json.loads(decoded['data'])
        self.assertEqual(len(data), len(EXECUTION_TIMES))
        for row in data:
            self.assertEqual(row['endpoint'], NAME)
            self.assertIn(row['execution_time'], EXECUTION_TIMES)
            self.assertEqual(row['version'], config.version)
            self.assertEqual(row['group_by'], GROUP_BY)
            self.assertEqual(row['ip'], IP)

    def test_get_json_monitor_rules(self):
        """
            Test whether the response is as it should be.
        """
        from flask_monitoringdashboard import config
        with self.app.test_client() as c:
            result = c.get('dashboard/get_json_monitor_rules').data
        decoded = jwt.decode(result, config.security_token, algorithms=['HS256'])
        data = json.loads(decoded['data'])
        self.assertEqual(len(data), 2)
        row = data[0]
        self.assertEqual(row['endpoint'], NAME)
        self.assertEqual(row['last_accessed'], str(TIMES[0]))
        self.assertTrue(row['monitor'])
        self.assertEqual(row['version_added'], config.version)

    def test_get_json_details(self):
        """
            Test whether the response is as it should be.
        """
        with self.app.test_client() as c:
            result = c.get('dashboard/get_json_details').data
        data = json.loads(result)
        import pkg_resources
        self.assertEqual(data['dashboard-version'], pkg_resources.require("Flask-MonitoringDashboard")[0].version)
