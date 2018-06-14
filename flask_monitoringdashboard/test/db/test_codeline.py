"""
    This file contains all unit tests that count a number of results in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/count.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.code_line import get_code_line

FN = 'filename'
LN = 42
FUN = 'fun'
CODE = 'code'


class TestCodeLine(unittest.TestCase):

    def test_get_code_line(self):
        with session_scope() as db_session:
            code_line1 = get_code_line(db_session, FN, LN, FUN, CODE)
            code_line2 = get_code_line(db_session, FN, LN, FUN, CODE)
            self.assertEqual(code_line1.id, code_line2.id)
            self.assertEqual(code_line1.function_name, code_line2.function_name)
            self.assertEqual(code_line1.filename, code_line2.filename)
            self.assertEqual(code_line1.line_number, code_line2.line_number)
            self.assertEqual(code_line1.code, code_line2.code)
