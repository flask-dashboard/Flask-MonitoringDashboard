import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count_group import (
    count_requests_group,
    count_requests_per_day,
)
from flask_monitoringdashboard.test.utils import (
    set_test_environment,
    clear_db,
    add_fake_data,
    TIMES,
)


class TestCountGroup(unittest.TestCase):
    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_count_requests_group(self):
        with session_scope() as db_session:
            self.assertEqual(count_requests_group(db_session), [(1, 5)])

    def test_count_requests_per_day(self):
        with session_scope() as db_session:
            self.assertEqual(count_requests_per_day(db_session, []), [])

            if TIMES[0].date() == TIMES[len(TIMES) - 1].date():  # must all be on the same day
                self.assertEqual(count_requests_per_day(db_session, [TIMES[0].date()]), [[(1, 5)]])
