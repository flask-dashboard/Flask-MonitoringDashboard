import unittest

from flask_monitoringdashboard.database.stack_line import add_stack_line, get_profiled_requests, \
    get_grouped_profiled_requests

from flask_monitoringdashboard.database import session_scope, StackLine
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, ENDPOINT_ID


class TestStackLine(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_stackline(self):
        with session_scope() as db_session:
            self.assertEqual(db_session.query(StackLine).all(), [])
            add_stack_line(db_session, request_id=1, position=0, indent=1, duration=1, code_line="code")
            self.assertNotEqual(db_session.query(StackLine).all(), [])

    def test_get_profiled_requests(self):
        with session_scope() as db_session:
            self.assertEqual(get_profiled_requests(db_session, endpoint_id=ENDPOINT_ID, offset=0, per_page=10), [])
            add_stack_line(db_session, request_id=ENDPOINT_ID, position=0, indent=1, duration=1, code_line="code")
            self.assertNotEqual(get_profiled_requests(db_session, endpoint_id=ENDPOINT_ID, offset=0, per_page=10), [])

    def test_get_grouped_profiled_requests(self):
        with session_scope() as db_session:
            self.assertEqual(get_grouped_profiled_requests(db_session, endpoint_id=ENDPOINT_ID), [])
            add_stack_line(db_session, request_id=ENDPOINT_ID, position=0, indent=1, duration=1, code_line="code")
            self.assertNotEqual(get_grouped_profiled_requests(db_session, endpoint_id=ENDPOINT_ID), [])
