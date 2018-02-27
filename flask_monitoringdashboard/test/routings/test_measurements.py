import unittest

from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, login


class TestMeasurement(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_overview(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/measurements/overview').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/measurements/overview').status_code)

    def test_heatmap(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/measurements/heatmap').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/measurements/heatmap').status_code)

    def test_page_number_of_requests_per_endpoint(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/measurements/requests').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/measurements/requests').status_code)

    def test_page_boxplot_per_version(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/measurements/versions').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/measurements/versions').status_code)

    def test_page_boxplot_per_endpoint(self):
        """
            Just retrieve the content and check if nothing breaks
        """
        self.assertEqual(302, self.app.get('dashboard/measurements/endpoints').status_code)
        login(self.app)
        self.assertEqual(200, self.app.get('dashboard/measurements/endpoints').status_code)

