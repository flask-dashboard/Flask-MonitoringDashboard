import unittest


class TestGroupBy(unittest.TestCase):

    def test_get_group_by(self):
        """
            Test whether the group_by returns the right result
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.core.group_by import get_group_by
        config.group_by = lambda: 3
        self.assertEqual(get_group_by(), '3')

        config.group_by = (lambda: 'User', lambda: 3.0)
        self.assertEqual(get_group_by(), '(User,3.0)')

        config.group_by = lambda: lambda: '1234'
        self.assertEqual(get_group_by(), '1234')

    def test_recursive_group_by(self):
        from flask_monitoringdashboard.core.group_by import recursive_group_by

        class Object(object):
            def __str__(self):
                return 'object'

        self.assertEqual(recursive_group_by(Object()), 'object')