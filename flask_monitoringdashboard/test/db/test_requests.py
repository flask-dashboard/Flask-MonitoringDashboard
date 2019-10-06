"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the
    file: 'flask_monitoringdashboard/database/function_calls.py')
    See info_box.py for how to run the test-cases.
"""

import time
import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.endpoint import get_avg_duration
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name
from flask_monitoringdashboard.test.utils import (
    set_test_environment,
    clear_db,
    add_fake_data,
    TIMES,
    NAME,
    IP,
    ENDPOINT_ID,
)


class TestRequest(unittest.TestCase):
    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_request(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.request import add_request

        name2 = 'main2'
        execution_time = 1234
        self.assertNotEqual(NAME, name2, 'Both cannot be equal, otherwise the test will fail')
        with session_scope() as db_session:
            endpoint = get_endpoint_by_name(db_session, name2)
            self.assertEqual(count_requests(db_session, endpoint.id), 0)
            add_request(
                db_session, execution_time, endpoint.id, ip=IP, group_by=None, status_code=200
            )
            self.assertEqual(count_requests(db_session, endpoint.id), 1)

    def test_get_versions(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.database.versions import get_versions

        with session_scope() as db_session:
            result = get_versions(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], config.version)

    def test_get_endpoints(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.endpoint import get_endpoints

        with session_scope() as db_session:
            result = get_endpoints(db_session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, NAME)

    def test_get_date_of_first_request(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.request import get_date_of_first_request

        with session_scope() as db_session:
            self.assertEqual(
                get_date_of_first_request(db_session), int(time.mktime(TIMES[0].timetuple()))
            )

    def test_get_avg_duration(self):
        with session_scope() as db_session:
            self.assertEqual(get_avg_duration(db_session, ENDPOINT_ID), 12000)
