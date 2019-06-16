import unittest
import datetime
import random

from flask_monitoringdashboard.core.reporting.date_interval import DateInterval
from flask_monitoringdashboard.core.reporting.make_report import make_report
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, ENDPOINT_ID, NAME, TIMES

START_OF_WEEK_1 = datetime.datetime(2019, 6, 1)
END_OF_WEEK_1 = START_OF_WEEK_1 + datetime.timedelta(days=7)

START_OF_WEEK_2 = datetime.datetime(2019, 5, 1)
END_OF_WEEK_2 = START_OF_WEEK_2 + datetime.timedelta(days=7)


class TestDateInterval(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()

        from flask_monitoringdashboard.database import session_scope, Request, Endpoint
        from flask_monitoringdashboard import config

        # Add requests
        with session_scope() as db_session:
            for i in range(100):
                # Slow requests in week 1
                db_session.add(Request(
                    endpoint_id=ENDPOINT_ID,
                    duration=1000,
                    version_requested=config.version,
                    time_requested=START_OF_WEEK_1 + datetime.timedelta(days=random.randint(0, 7)),
                    ip='192.168.0.1'))

                # Twice as fast requests in week 2
                db_session.add(Request(
                    endpoint_id=ENDPOINT_ID,
                    duration=500,
                    version_requested=config.version,
                    time_requested=START_OF_WEEK_2 + datetime.timedelta(days=random.randint(0, 7)),
                    ip='192.168.0.1'))

            # Add endpoint
            db_session.add(Endpoint(id=ENDPOINT_ID, name=NAME, monitor_level=1, time_added=datetime.datetime.utcnow(),
                                    version_added=config.version, last_requested=TIMES[0]))

    def test_stuff(self):
        now = datetime.datetime.utcnow()
        self.assertRaises(ValueError, lambda: DateInterval(now, now - datetime.timedelta(hours=5)))

        DateInterval(now, now + datetime.timedelta(hours=5))  # should not raise an error

        make_report(
            DateInterval(START_OF_WEEK_1, START_OF_WEEK_1 + datetime.timedelta(days=7)),
            DateInterval(START_OF_WEEK_2, START_OF_WEEK_2 + datetime.timedelta(days=7))
        )
