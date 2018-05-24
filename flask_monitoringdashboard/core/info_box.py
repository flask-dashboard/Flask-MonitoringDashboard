"""
    The following methods can be used for retrieving a HTML box with information:
      - get_plot_info: for information about the usage of a plot
      - get_rules_info: for information about the monitoring level.
"""

from flask_monitoringdashboard.core.forms import MONITOR_CHOICES

GRAPH_INFO = '''You can hover the graph with your mouse to see the actual values. You can also use 
the buttons at the top of the graph to select a subset of graph, scale it accordingly or save the graph
as a PNG image.'''


def b(s):
    return '<b>{}</b>'.format(s)


def p(s):
    return '<p>{}</p>'.format(s)


def get_plot_info(axes='', content=''):
    """
    :param axes: If specified, information about the axis
    :param content: If specified, information about the content
    :return: a String with information in HTML
    """

    information = b('Graph') + p(GRAPH_INFO)

    if axes:
        information += b('Axes') + p(axes)

    if content:
        information += b('Content') + p(content)

    return information


def get_rules_info():
    """ :return: a string with information in HTML """
    info = b(MONITOR_CHOICES[0][1]) + \
           p('When the monitoring-level is set to 0, you don\'t monitor anything about this endpoint. Only the time of '
             'the most recent request will be stored.')

    info += b(MONITOR_CHOICES[1][1]) + \
            p('When the monitoring-level is set to 1, you get all functionality from 0, plus functionality that '
              'collects data about the performance and utilization of this endpoint (as a black-box).')

    info += b(MONITOR_CHOICES[2][1]) + \
            p('When the monitoring-level is set to 2, you get all the functionality from 1, plus functionality that '
              'collects data about the performance and utilization of this endpoint per line of code. The data is only '
              'stored if the request is an outlier.')

    info += b(MONITOR_CHOICES[3][1]) + \
            p('When the monitoring-level is set to 3, you get all the functionality from 2, but now every request is '
              'stored in the database, instead of only outliers.')
    return info
