import datetime

import plotly
import plotly.graph_objs as go
from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times, get_num_requests
from flask_monitoringdashboard.database.function_calls import get_times, get_reqs_endpoint_day, get_versions, \
    get_data_per_version, get_endpoints, get_data_per_endpoint
from flask_monitoringdashboard.security import secure, is_admin


@blueprint.route('/measurements/overview')
@secure
def overview():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/measurement-overview.html', link=config.link, curr=2, times=get_times(),
                           colors=colors, access=get_last_accessed_times(), session=session, index=0,
                           is_admin=is_admin())


@blueprint.route('/measurements/heatmap')
@secure
def heatmap():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/measurement.html', link=config.link, curr=2, session=session, index=1,
                           graph=get_heatmap(end=None))


@blueprint.route('/measurements/requests')
@secure
def page_number_of_requests_per_endpoint():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/measurement.html', link=config.link, curr=2, session=session, index=2,
                           graph=get_stacked_bar())


@blueprint.route('/measurements/versions')
@secure
def page_boxplot_per_version():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/measurement.html', link=config.link, curr=2, session=session, index=3,
                           graph=get_boxplot_per_version())


@blueprint.route('/measurements/endpoints')
@secure
def page_boxplot_per_endpoint():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/measurement.html', link=config.link, curr=2, session=session, index=4,
                           graph=get_boxplot_per_endpoint())


def get_stacked_bar():
    data = get_reqs_endpoint_day()

    if len(data) == 0:
        return None

    labels = []
    endpoints = []
    # find labels and endpoints
    for d in data:
        if d.newTime not in labels:
            labels.append(d.newTime)
        if d.endpoint not in endpoints:
            endpoints.append(d.endpoint)
    labels.sort(reverse=True)

    # create dictionary. graph_data is in the form of: graph_data[label][endpoint]
    graph_data = {}
    for label in labels:
        graph_data[label] = {}
        for endpoint in endpoints:
            graph_data[label][endpoint] = 0

    # put data in dictionary
    for d in data:
        graph_data[d.newTime][d.endpoint] = d.cnt

    # create graph
    trace = []
    for endpoint in endpoints:

        lst = []
        for label in labels:
            lst.append(graph_data[label][endpoint])

        trace.append(go.Bar(
            y=labels,
            x=lst,
            name=endpoint,
            orientation='h',
            marker=dict(
                color=get_color(endpoint)
            )
        ))

    layout = go.Layout(
        barmode='stack',
        autosize=True,
        height=350 + 40 * len(labels),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=True,
        title='Number of requests per endpoint per day',
        xaxis=dict(title='Number of requests'),
        yaxis=dict(autorange='reversed')
    )

    return plotly.offline.plot(go.Figure(data=trace, layout=layout), output_type='div', show_link=False)


def get_boxplot_per_version():
    """
    Creates a graph with the execution times per version
    :return:
    """
    versions = get_versions()

    if len(versions) == 0:
        return None

    data = []
    for v in versions:
        values = [c.execution_time for c in get_data_per_version(v.version)]
        data.append(go.Box(
            x=values,
            marker=dict(
                color=get_color(v.version)
            ),
            name="{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M"))))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(autorange='reversed'),
        margin=go.Margin(
            l=200
        )
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)


def get_boxplot_per_endpoint():
    """
    Creates a graph with the execution times per endpoint
    :return:
    """
    endpoints = [str(e.endpoint) for e in get_endpoints()]

    data = []
    for endpoint in endpoints:
        values = [c.execution_time for c in get_data_per_endpoint(endpoint)]
        if len(values) == 0:
            continue
        data.append(go.Box(
            x=values,
            name=endpoint,
            marker=dict(
                color=get_color(endpoint)
            )
        ))

    if len(data) == 0:
        return None

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(endpoints),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every endpoint',
        xaxis=dict(title='Execution time (ms)'),
        margin=go.Margin(
            l=200
        )
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)


def get_heatmap(end):
    # list of hours: 1:00 - 23:00
    hours = ['0' + str(hour) + ':00' for hour in range(0, 10)] + \
            [str(hour) + ':00' for hour in range(10, 24)]

    data = get_num_requests(end)
    # list of days (format: year-month-day)
    days = [str(d.newTime[:10]) for d in data]
    # remove duplicates and sort the result
    days = sorted(list(set(days)))

    if len(data) == 0:
        return None

    first_day = max(datetime.datetime.strptime(days[0], '%Y-%m-%d'),
                    datetime.datetime.now() - datetime.timedelta(days=30))
    first_day -= datetime.timedelta(hours=12)
    last_day = datetime.datetime.strptime(days[len(days) - 1], '%Y-%m-%d') + datetime.timedelta(hours=12)

    # create empty 2D-dictionary with the keys: [hour][day]
    requests = {}
    for hour in hours:
        requests_day = {}
        for day in days:
            requests_day[day] = 0
        requests[hour] = requests_day

    # add data to the dictionary
    for d in data:
        day = str(d.newTime[:10])
        hour = str(d.newTime[11:16])
        requests[hour][day] = d.count

    # create a 2D-list out of the dictionary
    requests_list = []
    for hour in hours:
        day_list = []
        for day in days:
            day_list.append(requests[hour][day])
        requests_list.append(day_list)

    layout = go.Layout(
        autosize=True,
        height=800,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Heatmap of number of requests',
        xaxis=go.XAxis(range=[first_day, last_day],
                       title='Date'),
        yaxis=dict(title='Time', autorange='reversed')
    )

    trace = go.Heatmap(z=requests_list, x=days, y=hours)
    return plotly.offline.plot(go.Figure(data=[trace], layout=layout), output_type='div', show_link=False)
