"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/function_calls.py')
    See info_box.py for how to run the test-cases.
"""
import unittest
import datetime
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name, get_endpoints
from flask_monitoringdashboard.database.request import get_avg_duration, get_avg_duration_in_time_frame
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, TIMES, NAME, IP, \
    ENDPOINT_ID
import random


class TestAverageDurationInTimeFrame(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()

        from flask_monitoringdashboard.database import session_scope, Request, Endpoint
        from flask_monitoringdashboard import config

        # Add requests
        with session_scope() as db_session:
            for i in range(100):
                time_week_1 = datetime.datetime(2019, 6, 3)
                time_week_2 = datetime.datetime(2019, 5, 27)

                call = Request(endpoint_id=ENDPOINT_ID, duration=1000, version_requested=config.version,
                               time_requested=time_week_1 + datetime.timedelta(days=random.randint(0, 7)),
                               ip='192.168.0.1')
                db_session.add(call)

                call = Request(endpoint_id=ENDPOINT_ID, duration=500, version_requested=config.version,
                               time_requested=time_week_2 + datetime.timedelta(days=random.randint(0, 7)),
                               ip='192.168.0.1')

                db_session.add(call)

            # Add endpoint
            db_session.add(Endpoint(id=ENDPOINT_ID, name=NAME, monitor_level=1, time_added=datetime.datetime.utcnow(),
                                    version_added=config.version, last_requested=TIMES[0]))

    def test_add_request(self):
        with session_scope() as db_session:
            avg_in_week1 = get_avg_duration_in_time_frame(db_session, ENDPOINT_ID, datetime.datetime(2019, 6, 3),
                                                          datetime.datetime(2019, 6, 10))

            avg_in_week2 = get_avg_duration_in_time_frame(db_session, ENDPOINT_ID, datetime.datetime(2019, 5, 27),
                                                          datetime.datetime(2019, 6, 2))

            self.assertAlmostEqual(avg_in_week1, 1000)
            self.assertAlmostEqual(avg_in_week2, 500)
