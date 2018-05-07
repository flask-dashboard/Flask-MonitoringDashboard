"""
    Helper function for adding an argument to the **kwargs
"""
GRAPH_INFO = '''You can hover the graph with your mouse to see the actual values. You can also use 
the buttons at the top of the graph to select a subset of graph, scale it accordingly or save the graph
as a PNG image.'''


def add_default_value(arg_name, value, **kwargs):
    """ Add argument if it is not in the kwargs already """
    if arg_name not in kwargs.keys():
        kwargs[arg_name] = value
    return kwargs


def get_information(axes='', content=''):
    """
    :param axes: If specified, information about the axis
    :param content: If specified, information about the content
    :return: a String with information in HTML
    """
    def b(s):
        return '<b>{}</b>'.format(s)

    def p(s):
        return '<p>{}</p>'.format(s)

    information = b('Graph') + p(GRAPH_INFO)

    if axes:
        information = information + b('Axes') + p(axes)

    if content:
        information = information + b('Content') + p(content)

    return information
