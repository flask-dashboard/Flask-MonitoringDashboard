import datetime
import unittest

from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime


class TestTimezone(unittest.TestCase):

    def test_timezone(self):
        dt = datetime.datetime.now()
        self.assertEqual(to_local_datetime(to_utc_datetime(dt)), dt)
        self.assertEqual(to_utc_datetime(to_local_datetime(dt)), dt)

    def test_timezone_none(self):
        self.assertEqual(to_local_datetime(None), None)
        self.assertEqual(to_utc_datetime(None), None)
