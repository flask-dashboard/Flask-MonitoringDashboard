from unittest import TestCase
from dashboard.tests.test_first import FirstTestCase


class SecondTestCase(FirstTestCase, TestCase):

    def test_one(self):
        rv = FirstTestCase.api_get(self, '/')
        assert b'Redirecting...' in rv.data

    def test_two(self):
        rv = FirstTestCase.api_get(self, '/')
        assert b'Redirecting...' in rv.data

    def test_three(self):
        rv = FirstTestCase.api_get(self, '/')
        assert b'Redirecting...' in rv.data
        rv = FirstTestCase.api_get(self, '/')
        assert b'Redirecting...' in rv.data
