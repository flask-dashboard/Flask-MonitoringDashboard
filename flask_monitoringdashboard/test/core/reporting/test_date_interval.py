import unittest
import datetime

from flask_monitoringdashboard.core.reporting.date_interval import DateInterval


class TestDateInterval(unittest.TestCase):

    def test_start_date_must_come_before_end_date(self):
        now = datetime.datetime.utcnow()
        self.assertRaises(ValueError, lambda: DateInterval(now, now - datetime.timedelta(hours=5)))

        DateInterval(now, now + datetime.timedelta(hours=5))  # should not raise an error
