"""
    This file contains all unit tests for the endpoint-table in the database. (Corresponding to the file:
    'dashboard/database/function_calls.py')
    See __init__.py for how to run the test-cases.
"""

import unittest

from dashboard.test.utils import set_test_environment, clear_db, add_fake_data, mean, \
    EXECUTION_TIMES, TIMES, NAME, GROUP_BY, IP


class TestFunctionCall(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_get_reqs_endpoint_day(self):
        """
            Test whether the function returns the right values.
        """
        from dashboard.database.function_calls import get_reqs_endpoint_day
        result = get_reqs_endpoint_day()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cnt, len(EXECUTION_TIMES))
        self.assertEqual(result[0].endpoint, NAME)

    def test_add_function_call(self):
        """
            Test whether the function returns the right values.
        """
        from dashboard.database.function_calls import add_function_call, get_data_per_endpoint
        from dashboard.database import session_scope, FunctionCall
        name2 = 'main2'
        execution_time = 1234
        self.assertNotEqual(NAME, name2, 'Both cannot be equal, otherwise the test will fail')
        self.assertEqual(len(get_data_per_endpoint(name2)), 0)
        add_function_call(execution_time, name2, ip=IP)

        result2 = get_data_per_endpoint(name2)
        self.assertEqual(len(result2), 1)
        self.assertEqual(result2[0].endpoint, name2)
        self.assertEqual(result2[0].execution_time, execution_time)

        # Remove the data, such that the state of the db after this function is the same as before
        # with session_scope() as db_session:
        #     db_session.query(FunctionCall).filter(FunctionCall.endpoint == name2).delete()

    def test_2(self):
        return self.test_add_function_call()