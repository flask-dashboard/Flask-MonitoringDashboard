import unittest

from flask_monitoringdashboard.test.utils import get_test_app


class TestFactory(unittest.TestCase):

    def test_factory(self):
        """
            Create multiple applications and verify that the app doesn't break.
        """
        get_test_app()
        get_test_app()
