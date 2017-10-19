import unittest
from dashboard.main import user_app


class FirstTestCase(unittest.TestCase):
    def setUp(self):
        user_app.testing = True
        self.app = user_app.test_client()

    def api_get(self, link):
        return self.app.get(link)
