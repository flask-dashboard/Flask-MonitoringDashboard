import unittest

from flask_monitoringdashboard.core.profiler.util.stringHash import StringHash


class TestStringHash(unittest.TestCase):

    def test_stringhash(self):
        string_hash = StringHash()

        self.assertEqual(string_hash.hash('abc'), 0)
        self.assertEqual(string_hash.hash('def'), 1)
        self.assertEqual(string_hash.hash('abc'), 0)

    def test_unhash(self):
        string_hash = StringHash()
        self.assertEqual(string_hash.unhash(string_hash.hash('abc')), 'abc')
        self.assertRaises(ValueError, string_hash.unhash, 'unknown')