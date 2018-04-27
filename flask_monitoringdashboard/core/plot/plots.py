"""
    Contains all plots that are visible in the Dashboard
"""

import plotly.graph_objs as go
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.plot.util import add_default_value

BUBBLE_SIZE_RATIO = 2500


def heatmap(x, y, z, **kwargs):
    """
    :param x: list for labels of the x-values
    :param y: list for lables of the y-values
    :param z: 2D list with the actual data, encoded as: z[x-index][y-index]
    :param kwargs: additional arguments for the heatmap
    :return: a Heatmap that can be used for generating a Plotly figure :func:`get_figure`
    """
    return go.Heatmap(x=x, y=y, z=z, **kwargs)


def boxplot(values, **kwargs):
    """
    :param values: values for the boxplot
    :param kwargs: additional arguments for the boxplot
    :return: A boxplot that can be used for generating a Plotly figure :func:`get_figure`
    """
    if 'name' in kwargs.keys():
        kwargs = add_default_value('marker', {'color': get_color(kwargs.get('name', ''))}, **kwargs)
    kwargs = add_default_value('x', value=values, **kwargs)
    return go.Box(**kwargs)


def barplot(x, y, name, **kwargs):
    """
    :param x:
    :param y:
    :param name:
    :param kwargs: additional arguments
    :return: A barplot that can be used for generating a Plotly figure :func:`get_figure`
    """
    return go.Bar(
        x=x,
        y=y,
        name=name,
        orientation='h',
        marker={'color': get_color(name)},
        **kwargs
    )


def scatter(**kwargs):
    """

    :param kwargs: additional arguments for the scatterplot
    :return: a scatterplot that can be used for generating a Plotly figure :func:`get_figure`
    """
    return go.Scatter(**kwargs)


def get_average_bubble_size(data):
    """
    :param data: a list with lists: [[a, b, c], [d, e, f]]
    :return: a constant for the bubble size
    """
    def get_max(my_list):
        m = None
        for item in my_list:
            if isinstance(item, list):
                item = get_max(item)
            if not m or m < item:
                m = item
        return m
    return get_max(data) / BUBBLE_SIZE_RATIO
