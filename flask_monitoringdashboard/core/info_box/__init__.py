"""
    The following methods can be used for retrieving a HTML box with information:
      - get_plot_info: for information about the usage of a plot
      - get_rules_info: for information about the monitoring level.
"""
from flask_monitoringdashboard.core.plot.util import GRAPH_INFO


RULES_INFO = ''''''


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
        information = information + b('Axes') + p(axes)

    if content:
        information = information + b('Content') + p(content)

    return information


def get_rules_info():
    """ :return: a string with information in HTML """
    return RULES_INFO
