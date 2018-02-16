"""
    This is the main package for all test-cases.
    If you want to run all tests, then you can use this command:

        python -m unittest discover

    Another option is to run the main function at the bottom of this file.
"""
import os
import re
import sys
import unittest


def filename_to_modulename(filename):
    return os.path.splitext(filename)[0]


if __name__ == '__main__':
    # Finds all files that are located in a file named 'test_???.py', where ??? can be anything
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    regex = re.compile(r'test_.*\.py$')
    files = filter(regex.search, os.listdir(path))

    module_names = map(filename_to_modulename, files)
    modules = map(__import__, module_names)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for m in modules:
        suite.addTests(loader.loadTestsFromModule(m))

    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)

