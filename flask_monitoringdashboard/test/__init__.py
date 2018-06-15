"""
    This is the main package for all test-cases.
    If you want to run all tests, then you can use this command:

        python -m unittest discover

    Another option is to run the main function at the bottom of this file.
"""
import unittest


def get_test_suite():
    """
        Finds all files that are located in a file named 'test_*.py', where * can be anything
    """
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('flask_monitoringdashboard.test', pattern='test_*.py')
    return test_suite
