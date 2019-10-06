import unittest

from flask_monitoringdashboard.test.utils import (
    set_test_environment,
    clear_db,
    add_fake_data,
    get_test_app,
    test_admin_secure,
)


class TestExportData(unittest.TestCase):
    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_download_requests(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'download-requests')

    def test_download_outliers(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        test_admin_secure(self, 'download-outliers')
