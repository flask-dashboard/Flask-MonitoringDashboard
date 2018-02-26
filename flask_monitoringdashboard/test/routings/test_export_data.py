import unittest
import jwt

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, EXECUTION_TIMES, NAME, TIMES, GROUP_BY, \
    IP
from flask import Flask, json


class TestExportData(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        import flask_monitoringdashboard
        user_app = Flask(__name__)
        user_app.testing = True
        flask_monitoringdashboard.config.get_group_by = lambda: '12345'
        flask_monitoringdashboard.bind(app=user_app)
        clear_db()
        add_fake_data()
        self.app = user_app.test_client()

    def test_get_json_data_from(self):
        """
            Test whether the response is as it should be.
        """
        from flask_monitoringdashboard import config
        result = self.app.get('dashboard/get_json_data').data
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
        result = self.app.get('dashboard/get_json_monitor_rules').data
        decoded = jwt.decode(result, config.security_token, algorithms=['HS256'])
        data = json.loads(decoded['data'])
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertEqual(row['endpoint'], NAME)
        self.assertEqual(row['last_accessed'], u'None')
        self.assertTrue(row['monitor'])
        self.assertEqual(row['version_added'], config.version)

    def test_get_json_details(self):
        """
            Test whether the response is as it should be.
        """
        result = self.app.get('dashboard/get_json_details').data
        data = json.loads(result)
        import pkg_resources
        self.assertEqual(data['version'], pkg_resources.require("Flask-MonitoringDashboard")[0].version)
