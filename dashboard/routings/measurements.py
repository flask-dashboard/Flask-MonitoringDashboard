import datetime

import plotly
import plotly.graph_objs as go
import pygal
from flask import session, render_template

from dashboard import blueprint, config
from dashboard.database.endpoint import get_last_accessed_times, get_num_requests
from dashboard.database.function_calls import get_times, get_reqs_endpoint_day, get_versions, get_data_per_version, \
    get_endpoints, get_data_per_endpoint
from dashboard.security import secure


@blueprint.route('/measurements/0')
@secure
def page_heatmap():
    return render_template('measurements/plotly.html', link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session, index=0, graph=get_heatmap(end=None))


@blueprint.route('/measurements/1')
@secure
def page_number_of_requests_per_endpoint():
    return render_template('measurements/pygal.html', link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session, index=1, graph=get_stacked_bar())


@blueprint.route('/measurements/2')
@secure
def page_boxplot_per_version():
    return render_template('measurements/plotly.html', link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session, index=2, graph=get_boxplot_per_version())


@blueprint.route('/measurements/3')
@secure
def page_boxplot_per_endpoint():
    return render_template('measurements/plotly.html', link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session, index=3, graph=get_boxplot_per_endpoint())


def get_stacked_bar():
    data = get_reqs_endpoint_day()
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
    graph = pygal.graph.horizontalstackedbar.HorizontalStackedBar(height=100 + len(labels) * 15)
    graph.title = 'Number of requests per endpoint per day'
    graph.x_labels = labels

    # put data (from dictionary) in graph
    for endpoint in endpoints:
        lst = []
        for label in labels:
            lst.append(graph_data[label][endpoint])
        graph.add(endpoint, lst)

    return graph.render_data_uri()


def get_boxplot_per_version():
    """
    Creates a graph with the execution times per version
    :return:
    """
    versions = get_versions()

    data = []
    for v in versions:
        values = [c.execution_time for c in get_data_per_version(v.version)]
        data.append(go.Box(x=values, name="{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M"))))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(tickangle=-50, autorange='reversed')
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)


def get_boxplot_per_endpoint():
    """
    Creates a graph with the execution times per endpoint
    :return:
    """
    endpoints = [str(e.endpoint) for e in get_endpoints()]

    data = []
    for e in endpoints:
        values = [c.execution_time for c in get_data_per_endpoint(e)]
        if len(e) > 16:
            e = '...' + e[-14:]
        data.append(go.Box(x=values, name=e))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(endpoints),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every endpoint',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(tickangle=-45)
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
    if len(days) > 0:
        first_day = max(datetime.datetime.strptime(days[0], '%Y-%m-%d'),
                        datetime.datetime.now() - datetime.timedelta(days=30))
        last_day = datetime.datetime.strptime(days[len(days)-1], '%Y-%m-%d')
    else:
        first_day = datetime.datetime.now() - datetime.timedelta(days=30)
        last_day = datetime.datetime.now()

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
