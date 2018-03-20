import unittest

from flask_monitoringdashboard.test.utils import get_test_app


class TestConfig(unittest.TestCase):

    def test_init(self):
        """
            Test whether the init_form doesn't break when nothing is specified
        """
        import flask_monitoringdashboard as dashboard
        dashboard.config.init_from()
