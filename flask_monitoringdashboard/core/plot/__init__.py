"""
    Contains all code for generating plots
    This files ensures consistency for all plots
"""
import plotly
import plotly.graph_objs as go
from flask_monitoringdashboard.core.plot.util import add_default_value
from flask_monitoringdashboard.core.plot.plots import heatmap, boxplot, barplot, scatter, get_average_bubble_size


def get_layout(**kwargs):
    """
    :param kwargs: additional arguments for the layout
    :return: a Plotly Layout object with the required values
    """
    kwargs = add_default_value('showlegend', False, **kwargs)
    kwargs = add_default_value('autosize', True, **kwargs)
    kwargs = add_default_value('plot_bgcolor', 'rgba(249,249,249,1)', **kwargs)
    kwargs = add_default_value('height', 700, **kwargs)
    kwargs = add_default_value('hovermode', 'closest', **kwargs)
    return go.Layout(**kwargs)


def get_margin(**kwargs):
    """
    :param kwargs: additional arguments for the Margin object
    :return: a Plotly Margin instance
    """
    kwargs = add_default_value('l', 200, **kwargs)
    return go.Margin(**kwargs)


def get_figure(layout, data, **kwargs):
    """
    :param layout: must be a Plotly Layout instance
    :param data: the data for the
    :param kwargs: additional arguments for the plot
    :return: A plotly generated plot with the required data
    """
    if not data:
        return None
    kwargs = add_default_value('output_type', 'div', **kwargs)
    kwargs = add_default_value('show_link', False, **kwargs)
    return plotly.offline.plot(go.Figure(data=data, layout=layout), **kwargs)
