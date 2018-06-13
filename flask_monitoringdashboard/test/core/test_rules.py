import unittest

from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, NAME


class TestRules(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_rules(self):
        with self.app.app_context():
            self.assertEqual(len(get_rules()), 2)
            self.assertEqual(len(get_rules(NAME)), 1)
            self.assertEqual(get_rules('unknown'), [])
