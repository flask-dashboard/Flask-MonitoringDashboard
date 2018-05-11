import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, NAME, \
    test_admin_secure


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
        test_admin_secure(self, 'endpoint/{}/hourly_load'.format(NAME))

    def test_result_time_per_version_per_user(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'endpoint/{}/version_user'.format(NAME))

    def test_result_time_per_version_per_ip(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'endpoint/{}/version_ip'.format(NAME))

    def test_result_time_per_version(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'endpoint/{}/versions'.format(NAME))

    def test_result_time_per_user(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'endpoint/{}/users'.format(NAME))

    def test_result_outliers(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'endpoint/{}/outliers'.format(NAME))
