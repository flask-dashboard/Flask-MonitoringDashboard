"""
    Helper function for adding an argument to the **kwargs
"""


def add_default_value(arg_name, value, **kwargs):
    """ Add argument if it is not in the kwargs already """
    if arg_name not in kwargs.keys():
        kwargs[arg_name] = value
    return kwargs


