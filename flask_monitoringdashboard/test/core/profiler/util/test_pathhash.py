import unittest

from flask_monitoringdashboard.core.profiler.util import PathHash
from flask_monitoringdashboard.database import StackLine, CodeLine

FN = 'filename0'
LN = 42

STACK_LINES = [
            StackLine(request_id=0, position=0, indent=0, duration=1010,
                      code=CodeLine(filename=FN, line_number=0, function_name='None', code='f()')),
            StackLine(request_id=0, position=1, indent=1, duration=500,
                      code=CodeLine(filename=FN, line_number=1, function_name='f', code='sleep(1)')),
            StackLine(request_id=0, position=1, indent=1, duration=510,
                      code=CodeLine(filename=FN, line_number=2, function_name='f', code='sleep(1.01)'))]


class TestPathHash(unittest.TestCase):

    def setUp(self):
        self.path = PathHash()

    def test_get_path(self):
        self.assertEqual(self.path.get_path(FN, LN), '0:42')

    def test_append(self):
        self.path.get_path(FN, LN)
        self.assertEqual(self.path.append(FN, LN), '0:42->0:42')

    def test_encode(self):
        self.assertEqual(self.path._encode(FN, LN), '0:42')

    def test_decode(self):
        self.assertEqual(self.path._decode(self.path._encode(FN, LN)), (FN, LN))

    def test_get_indent(self):
        self.assertEqual(self.path.get_indent(''), 0)
        self.assertEqual(self.path.get_indent('0:42'), 1)
        self.assertEqual(self.path.get_indent('0:42->0:42'), 2)

    def test_get_last_fn_ln(self):
        self.assertEqual(self.path.get_last_fn_ln(self.path._encode(FN, LN)), (FN, LN))

    def test_get_code(self):
        for index, item in enumerate(STACK_LINES):
            path = self.path.get_stacklines_path(STACK_LINES, index)
            self.assertEqual(self.path.get_code(path), item.code.code)

    def test_get_stacklines_path(self):
        self.assertEqual(self.path.get_stacklines_path(STACK_LINES, 0), '1:0')
        self.assertEqual(self.path.get_stacklines_path(STACK_LINES, 1), '1:0->1:2')
        self.assertEqual(self.path.get_stacklines_path(STACK_LINES, 2), '1:0->1:3')
