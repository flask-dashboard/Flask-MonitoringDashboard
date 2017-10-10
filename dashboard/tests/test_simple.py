import unittest
import requests


class MyTestCase(unittest.TestCase):
    def test_something(self):
        r = requests.get('http://0.0.0.0:5000/')
        self.assertEqual(200, r.status_code)

    def test_somethingElse(self):
        r = requests.get('http://0.0.0.0:5000/')
        self.assertEqual(200, r.status_code)

    def test_indexHit(self):
        r = requests.get('http://0.0.0.0:5000/')
        self.assertEqual(200, r.status_code)
        r = requests.get('http://0.0.0.0:5000/static/assets/js/custom.js')
        self.assertEqual(200, r.status_code)


if __name__ == '__main__':
    unittest.main()
