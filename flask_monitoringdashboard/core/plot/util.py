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


