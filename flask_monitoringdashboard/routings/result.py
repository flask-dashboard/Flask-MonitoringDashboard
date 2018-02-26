import datetime
import math
import plotly
import plotly.graph_objs as go

from flask import session, url_for, render_template, request
from flask_wtf import FlaskForm
from werkzeug.routing import BuildError
from wtforms import SelectMultipleField, SubmitField

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule, \
    get_line_results, get_all_measurement_per_column, get_endpoint_column_user_sorted, get_all_measurement
from flask_monitoringdashboard.database.function_calls import get_versions
from flask_monitoringdashboard.security import secure
from flask_monitoringdashboard.routings.measurements import get_heatmap
from flask_monitoringdashboard.database.outlier import get_outliers
from flask_monitoringdashboard.colors import get_color

# Constants
BUBBLE_SIZE_RATIO = 1250


@blueprint.route('/result/<end>/heatmap')
@secure
def result_heatmap(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    return render_template('endpoint/plotly.html', link=config.link, session=session, rule=rule, url=url,
                           graph=get_heatmap(end), end=end, index=0)


@blueprint.route('/result/<end>/time_per_hour')
@secure
def result_time_per_hour(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    return render_template('endpoint/plotly.html', link=config.link, session=session, rule=rule, url=url,
                           graph=get_time_per_hour(end), end=end, index=1)


@blueprint.route('/result/<end>/hits_per_hour')
@secure
def result_hits_per_hour(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    return render_template('endpoint/plotly.html', link=config.link, session=session, rule=rule, url=url,
                           graph=get_hits_per_hour(end), end=end, index=2)


@blueprint.route('/result/<end>/time_per_version_per_user', methods=['GET', 'POST'])
@secure
def result_time_per_version_per_user(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    graph, form = get_time_per_version_per_user(end, get_versions(end))
    return render_template('endpoint/time_per_user.html', link=config.link, session=session, rule=rule, url=url,
                           graph=graph, form=form, end=end, index=3)


@blueprint.route('/result/<end>/time_per_version_per_ip', methods=['GET', 'POST'])
@secure
def result_time_per_version_per_ip(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    graph, form = get_time_per_version_per_ip(end, get_versions(end))
    return render_template('endpoint/time_per_user.html', link=config.link, session=session, rule=rule, url=url,
                           graph=graph, form=form, end=end, index=4)


@blueprint.route('/result/<end>/time_per_version')
@secure
def result_time_per_version(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    return render_template('endpoint/plotly.html', link=config.link, session=session, rule=rule, url=url,
                           graph=get_time_per_version(end, get_versions(end)), end=end, index=5)


@blueprint.route('/result/<end>/time_per_user', methods=['GET', 'POST'])
@secure
def result_time_per_user(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    graph, form = get_time_per_user(end)
    return render_template('endpoint/time_per_user.html', link=config.link, session=session, rule=rule, url=url,
                           graph=graph, form=form, end=end, index=6)


@blueprint.route('/result/<end>/outliers')
@secure
def result_outliers(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    return render_template('endpoint/outliers.html', link=config.link, session=session, rule=rule, url=url,
                           end=end, index=7, table=get_outliers(end))


def formatter(ms):
    """
    formats the ms into seconds and ms
    :param ms: the number of ms
    :return: a string representing the same amount, but now represented in seconds and ms.
    """
    sec = int(ms) // 1000
    ms = int(ms) % 1000
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}.{1}s'.format(sec, ms)


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

    # Find the last date which contains data
    max_time = max([d.newTime for d in data])
    max_date = datetime.datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
    max_date += datetime.timedelta(minutes=30)

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

    graph = [trace3, trace2, trace1]

    layout = go.Layout(
        autosize=True,
        height=600,
        title='Execution time (minimum, average and maximum) per hour',
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=True,
        barmode='overlay',
        xaxis=go.XAxis(
            title='Date',
            range=[max_date - datetime.timedelta(days=2), max_date]
        ),
        yaxis=go.YAxis(
            title='Execution time (ms)'
        )
    )
    return plotly.offline.plot(go.Figure(data=graph, layout=layout), output_type='div', show_link=False)


def get_hits_per_hour(end):
    data = get_line_results(end)

    # Find the last date which contains data
    max_time = max([d.newTime for d in data])
    max_date = datetime.datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
    max_date += datetime.timedelta(minutes=30)

    graph = [go.Bar(
        x=[d.newTime for d in data],
        y=[d.count for d in data],
        marker=dict(color=get_color(end))
    )]

    layout = go.Layout(
        autosize=True,
        height=600,
        title='Number of hits per hour',
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        xaxis=go.XAxis(
            title='Date',
            range=[max_date - datetime.timedelta(days=2), max_date]
        ),
        yaxis=go.YAxis(title='Hits')
    )
    return plotly.offline.plot(go.Figure(data=graph, layout=layout), output_type='div', show_link=False)


def get_time_per_version_per_user(end, versions):
    user_data = {}
    data = [t.execution_time for t in get_all_measurement(end)]
    # compute the average for determining the size of the bubbles in the plot
    average = math.sqrt(sum(data) / len(data)) / BUBBLE_SIZE_RATIO

    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        user_data[d] = {}
        for v in versions:
            user_data[d][v.version] = 0

    form, selection = get_form(user_data)
    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.group_by):
        user_data[str(d.group_by)][d.version] = d.average

    db_data = [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]
    trace = []
    for d in db_data:  # iterate through all (unique) ip addresses
        if selection == [] or d in selection:
            data = []
            for version in versions:
                data.append(user_data[d][version.version])

            hover_text = []
            for i in range(len(data)):
                hover_text.append('Version: ' + versions[i].version + '<br>Time: ' + formatter(data[i]))

            trace.append(go.Scatter(
                x=["{0}<br>{1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions],
                hovertext=hover_text,
                y=[d] * len(versions),
                name=d,
                mode='markers',
                marker=dict(
                    color=[get_color(d)] * len(versions),
                    size=[math.sqrt(d) for d in data],
                    sizeref=average,
                    sizemode='area'
                )
            ))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(trace),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Average execution time for every user per version',
        xaxis=dict(
            title='Versions',
            type='category'
        ),
        yaxis=dict(
            type='category',
            title='Users',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200,
            b=200
        )
    )

    return plotly.offline.plot(go.Figure(data=trace, layout=layout), output_type='div', show_link=False), form


def get_form(data):
    # create a form to make a selection
    choices = []
    for d in list(data):
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

    return form, selection


def get_time_per_version_per_ip(end, versions):
    ip_data = {}
    data = [t.execution_time for t in get_all_measurement(end)]
    # compute the average for determining the default size
    average = math.sqrt(sum(data) / len(data)) / 1250
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        ip_data[d] = {}
        for v in versions:
            ip_data[d][v.version] = 0

    form, selection = get_form(ip_data)

    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.ip):
        ip_data[str(d.ip)][d.version] = d.average

    db_data = [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]
    trace = []
    for d in db_data:  # iterate through all (unique) ip addresses
        if selection == [] or d in selection:
            data = []
            for version in versions:
                data.append(ip_data[d][version.version])

            hover_text = []
            for i in range(len(data)):
                hover_text.append('Version: ' + versions[i].version + '<br>Time: ' + formatter(data[i]))

            trace.append(go.Scatter(
                x=["{0}<br>{1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions],
                hovertext=hover_text,
                y=[d] * len(versions),
                name=d,
                mode='markers',
                marker=dict(
                    color=[get_color(d)] * len(versions),
                    size=[math.sqrt(d) for d in data],
                    sizeref=average,
                    sizemode='area'
                )
            ))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(trace),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Average execution time for every IP-address per version',
        xaxis=dict(
            title='Versions',
            type='category'
        ),
        yaxis=dict(
            type='category',
            title='IP-addresses',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200,
            b=200
        )
    )

    return plotly.offline.plot(go.Figure(data=trace, layout=layout), output_type='div', show_link=False), form


def get_time_per_version(end, versions):
    data = []
    for v in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=v.version)]

        data.append(go.Box(
            x=values,
            marker=dict(
                color=get_color(end)
            ),
            name="{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M"))))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(
            title='Version',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200
        )
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)


def get_time_per_user(end):
    users = [str(c.group_by) for c in get_endpoint_column_user_sorted(endpoint=end, column=FunctionCall.group_by)]
    form, selection = get_form(users)
    data = []
    for user in users:
        if selection == [] or user in selection:
            values = [str(c.execution_time) for c in
                      get_all_measurement_per_column(endpoint=end, column=FunctionCall.group_by, value=user)]
            data.append(go.Box(
                x=values,
                marker=dict(
                    color=get_color(user)
                ),
                name='{0}  -'.format(user)))
    data.reverse()
    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(data),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every user',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(title='User')
    )
    graph = plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
    return graph, form
