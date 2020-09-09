from flask_monitoringdashboard.core.group_by import get_group_by, recursive_group_by


def test_get_group_by_function(config):
    """Test whether the group_by returns the right result."""
    config.group_by = lambda: 3
    assert get_group_by() == '3'


def test_get_group_by_tuple(config):
    config.group_by = (lambda: 'User', lambda: 3.0)
    assert get_group_by() == '(User,3.0)'


def test_get_group_by_function_in_function(config):
    config.group_by = lambda: lambda: '1234'
    assert get_group_by() == '1234'


def test_recursive_group_by():
    class Object(object):
        def __str__(self):
            return 'object'

    assert recursive_group_by(Object()) == 'object'
