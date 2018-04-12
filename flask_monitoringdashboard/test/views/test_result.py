import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, login, \
    NAME


class TestResult(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_result_heatmap(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/heatmap'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/heatmap'.format(NAME)).status_code)

    def test_result_time_per_hour(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/time_per_hour'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/time_per_hour'.format(NAME)).status_code)

    def test_result_hits_per_hour(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/hits_per_hour'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/hits_per_hour'.format(NAME)).status_code)

    def test_result_time_per_version_per_user(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/time_per_version_per_user'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/time_per_version_per_user'.format(NAME)).status_code)

    def test_result_time_per_version_per_ip(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/time_per_version_per_ip'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/time_per_version_per_ip'.format(NAME)).status_code)

    def test_result_time_per_version(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/time_per_version'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/time_per_version'.format(NAME)).status_code)

    def test_result_time_per_user(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/time_per_user'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/time_per_user'.format(NAME)).status_code)

    def test_result_outliers(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/result/{}/outliers'.format(NAME)).status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/result/{}/outliers'.format(NAME)).status_code)