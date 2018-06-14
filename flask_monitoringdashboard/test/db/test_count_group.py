import datetime
import unittest

from flask_monitoringdashboard.database import session_scope, TestEndpoint
from flask_monitoringdashboard.database.count_group import get_latest_test_version, count_requests_group, \
    count_times_tested, count_requests_per_day
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, ENDPOINT_ID, \
    add_fake_test_runs, NAME, TIMES


class TestCountGroup(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    @staticmethod
    def add_test_data(db_session):
        add_fake_test_runs()
        db_session.add(TestEndpoint(endpoint_id=ENDPOINT_ID, test_id=1, duration=1234, app_version="1.0",
                                    travis_job_id="1", time_added=datetime.datetime.utcnow()))
        db_session.add(TestEndpoint(endpoint_id=ENDPOINT_ID, test_id=1, duration=2345, app_version="1.0",
                                    travis_job_id="1", time_added=datetime.datetime.utcnow()))

    def test_get_latest_test_version(self):
        with session_scope() as db_session:
            self.assertIsNone(get_latest_test_version(db_session))
            self.add_test_data(db_session)
            self.assertEqual(get_latest_test_version(db_session), "1.0")

    def test_count_requests_group(self):
        with session_scope() as db_session:
            self.assertEqual(count_requests_group(db_session), [(1, 5)])

    def test_count_times_tested(self):
        with session_scope() as db_session:
            self.assertEqual(count_times_tested(db_session), [])
            self.add_test_data(db_session)
            self.assertEqual(count_times_tested(db_session), [(NAME, 2)])

    def test_count_requests_per_day(self):
        with session_scope() as db_session:
            self.assertEqual(count_requests_per_day(db_session, []), [])

            if TIMES[0].date() == TIMES[len(TIMES)-1].date():  # must all be on the same day
                self.assertEqual(count_requests_per_day(db_session, [TIMES[0].date()]), [[(1, 5)]])
