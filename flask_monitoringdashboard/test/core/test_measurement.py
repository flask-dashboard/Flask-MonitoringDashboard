import unittest

from flask_monitoringdashboard.database import Endpoint
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, get_test_app, NAME


class TestMeasurement(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        self.app = get_test_app()

    def test_init_measurement(self):
        from flask_monitoringdashboard.core.measurement import init_measurement
        with self.app.app_context():
            init_measurement()

    def test_add_decorator(self):
        from flask_monitoringdashboard.core.measurement import add_decorator
        with self.app.app_context():
            for i in range(4):
                self.assertEqual(add_decorator(Endpoint(name=NAME, monitor_level=i)), None)
            self.assertRaises(ValueError, add_decorator, Endpoint(name=NAME, monitor_level=-1))
