from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.logger import log

PRIMITIVES = (bool, bytes, float, int, str)


def recursive_group_by(argument):
    """
    Returns the result of the given argument. The result is computed as:
    - If the argument is a primitive (i.e. str, bool, int, ...) return its value.
    - If the argument is a function, call the function.
    - If the argument is iterable (i.e. list or tuple), compute the result by iterating over the
        argument
    Return type is always a string
    """

    if type(argument) in PRIMITIVES:
        return str(argument)

    if callable(argument):
        return recursive_group_by(argument())

    # Try if the argument is iterable (i.e. tuple or list)
    try:
        result_list = [recursive_group_by(i) for i in argument]
        result_string = ','.join(result_list)
        return '({})'.format(result_string)
    except TypeError:
        # Cannot deal with this
        return str(argument)


def get_group_by():
    """
    :return: a string with the value
    """
    group_by = None
    try:
        if config.group_by:
            group_by = recursive_group_by(config.group_by)
    except Exception as e:
        log('Can\'t execute group_by function: {}'.format(e))
    return str(group_by)
