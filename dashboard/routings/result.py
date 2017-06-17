import datetime
import math

import plotly
import plotly.graph_objs as go
import pygal
from flask import session, url_for, render_template, request
from flask_wtf import FlaskForm
from werkzeug.routing import BuildError
from wtforms import SelectMultipleField, SubmitField

from dashboard import blueprint, config
from dashboard.database import FunctionCall
from dashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule, \
    get_line_results, get_all_measurement_per_column, get_endpoint_column_user_sorted
from dashboard.database.function_calls import get_versions
from dashboard.security import secure
from dashboard.routings.measurements import get_heatmap


@blueprint.route('/result/<end>/<int:index>', methods=['GET', 'POST'])
@secure
def result(end, index=0):
    rule = get_monitor_rule(end)
    url = get_url(end)

    # returns a page with the time per hour
    if index == 1:
        page = 'endpoint/endpoint_plotly.html'
        graph = get_time_per_hour(end)

    # returns a page with the number of hits per hour
    elif index == 2:
        page = 'endpoint/endpoint_plotly.html'
        graph = get_hits_per_hour(end)

    # returns a page with the time per version per user
    elif index == 3:
        graph, form = get_time_per_version_per_user(end, get_versions(end))
        return render_template('endpoint/endpoint_with_selection.html', link=config.link, session=session, rule=rule,
                               url=url, graph=graph, end=end, index=index, form=form)

    # returns a page with the time per version per ip
    elif index == 4:
        graph, form = get_time_per_version_per_ip(end, get_versions(end))
        return render_template('endpoint/endpoint_with_selection.html', link=config.link, session=session, rule=rule,
                               url=url, graph=graph, end=end, index=index, form=form)

    # returns a page with the time per version
    elif index == 5:
        page = 'endpoint/endpoint_plotly.html'
        graph = get_time_per_version(end, get_versions(end))

    # returns a page with the time per user
    elif index == 6:
        page = 'endpoint/endpoint_plotly.html'
        graph = get_time_per_user(end)

    # default: return a page with the heatmap
    else:
        index = 0
        page = 'endpoint/endpoint_plotly.html'
        graph = get_heatmap(end)

    return render_template(page, link=config.link, session=session, rule=rule, url=url, graph=graph, end=end,
                           index=index)


def formatter(ms):
    """
    formats the ms into seconds and ms
    :param ms: the number of ms
    :return: a string representing the same amount, but now represented in seconds and ms.
    """
    sec = math.floor(ms / 1000)
    ms = round(ms % 1000, 2)
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}s and {1}ms'.format(sec, ms)


def get_url(end):
    """
    Returns the URL if possible.
    URL's that require additional arguments, like /static/<file> cannot be retrieved.
    :param end: the endpoint for the url.
    :return: the url_for(end) or None,
    """
    try:
        return url_for(end)
    except BuildError:
        return None


def get_time_per_hour(end):
    data = get_line_results(end)

    trace1 = go.Bar(
        x=[d.newTime for d in data],
        y=[d.min for d in data],
        name='Minimum'
    )

    trace2 = go.Bar(
        x=[d.newTime for d in data],
        y=[d.avg for d in data],
        name='Average'
    )

    trace3 = go.Bar(
        x=[d.newTime for d in data],
        y=[d.max for d in data],
        name='Maximum'
    )

    graph = [trace1, trace2, trace3]

    layout = go.Layout(
        autosize=False,
        width=900,
        height=600,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=True,
        barmode='group',
        xaxis=go.XAxis(range=[datetime.datetime.now() - datetime.timedelta(days=2), datetime.datetime.now()])
    )
    return plotly.offline.plot(go.Figure(data=graph, layout=layout), output_type='div', show_link=False)


def get_hits_per_hour(end):
    data = get_line_results(end)
    graph = [go.Bar(
        x=[d.newTime for d in data],
        y=[d.count for d in data]
    )]

    layout = go.Layout(
        autosize=False,
        width=900,
        height=600,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        xaxis=go.XAxis(range=[datetime.datetime.now() - datetime.timedelta(days=7), datetime.datetime.now()])
    )
    return plotly.offline.plot(go.Figure(data=graph, layout=layout), output_type='div', show_link=False)


def get_time_per_version_per_user(end, versions):
    user_data = {}
    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        user_data[d] = {}
        for v in versions:
            user_data[d][v.version] = 0

    # create a form to select users
    choices = []
    for d in list(user_data):
        choices.append((d, d))

    class SelectionForm(FlaskForm):
        selection = SelectMultipleField(
            'Pick Things!',
            choices=choices,
        )
        submit = SubmitField('Render graph')

    form = SelectionForm(request.form)
    selection = []
    if request.method == 'POST':
        selection = [str(item) for item in form.data['selection']]

    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.group_by):
        user_data[str(d.group_by)][d.version] = d.average

    # dot chart
    graph = pygal.Dot(x_label_rotation=30, show_legend=False, height=200 + len(user_data) * 40)
    graph.x_labels = ["{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions]

    # add rows to the charts
    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        data = []
        # render full graph if no selection is made, else render only the users that are selected
        if selection == [] or d in selection:
            for v in versions:
                data.append(user_data[d][v.version])
            graph.add(d, data, formatter=formatter)
    return graph.render_data_uri(), form


def get_time_per_version_per_ip(end, versions):
    ip_data = {}
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        ip_data[d] = {}
        for v in versions:
            ip_data[d][v.version] = 0

    # create a form to select users
    choices = []
    for d in list(ip_data):
        choices.append((d, d))

    class SelectionForm(FlaskForm):
        selection = SelectMultipleField(
            'Pick Things!',
            choices=choices,
        )
        submit = SubmitField('Render graph')

    form = SelectionForm(request.form)
    selection = []
    if request.method == 'POST':
        selection = [str(item) for item in form.data['selection']]

    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.ip):
        ip_data[str(d.ip)][d.version] = d.average

    # dot chart
    graph = pygal.Dot(x_label_rotation=30, show_legend=False, height=200 + len(ip_data) * 40)
    graph.x_labels = ["{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions]

    # add rows to the charts
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        data = []
        # render full graph if no selection is made, else render only the users that are selected
        if selection == [] or d in selection:
            for v in versions:
                data.append(ip_data[d][v.version])
            graph.add(d, data, formatter=formatter)
    return graph.render_data_uri(), form


def get_time_per_version(end, versions):
    data = []
    for v in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=v.version)]

        data.append(go.Box(x=values, name="{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M"))))

    layout = go.Layout(
        autosize=False,
        width=900,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(tickangle=-50, autorange='reversed')
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)


def get_time_per_user(end):
    users = [str(c.group_by) for c in get_endpoint_column_user_sorted(endpoint=end, column=FunctionCall.group_by)]
    data = []
    for u in users:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.group_by, value=u)]
        data.append(go.Box(x=values, name='{0}  -'.format(u)))

    layout = go.Layout(
        autosize=False,
        width=900,
        height=350 + 40 * len(users),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every user',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(title='User')
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
