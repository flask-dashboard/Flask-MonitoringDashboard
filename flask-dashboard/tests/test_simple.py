import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_somethingElse(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
