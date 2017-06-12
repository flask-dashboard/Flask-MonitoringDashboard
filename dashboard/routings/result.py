import pygal
import math
from flask import session, url_for, render_template
from werkzeug.routing import BuildError

from dashboard import blueprint, config
from dashboard.database import FunctionCall
from dashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule, \
    get_last_accessed_times, get_line_results, get_all_measurement_per_column, get_num_requests, \
    get_endpoint_column_user_sorted
from dashboard.database.function_calls import get_times, get_data_per_version, get_versions, get_reqs_endpoint_day
from dashboard.security import secure

import plotly
import plotly.graph_objs as go


@blueprint.route('/measurements')
@secure
def measurements():
    return render_template('measurements.html', link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session,
                           heatmap=get_heatmap(end=None), etpv=get_boxplot_per_version(), rpepd=get_stacked_bar())


def get_boxplot_per_version():
    """
    Creates a graph with the execution times per version
    :return:
    """
    versions = [str(v.version) for v in get_versions()]

    data = []
    for v in versions:
        values = [c.execution_time for c in get_data_per_version(v)]
        data.append(go.Box(x=values, name=v))

    layout = go.Layout(
        autosize=False,
        width=900,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(title='Version')
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)


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


def get_graphs_per_hour(end):
    """
    Function that builds two graphs:
    1. Execution time (in ms) grouped by hour
    2. Number of hits grouped by hour.
    :param end: the endpoint
    :return: graph1, graph2
    """
    data = get_line_results(end)
    graph1 = pygal.HorizontalBar(height=100 + len(data) * 30)
    graph1.x_labels = []
    list_avg = []
    list_min = []
    list_max = []
    list_count = []
    for d in data:
        graph1.x_labels.append(d.newTime)
        list_min.append(d.min)
        list_avg.append(d.avg)
        list_max.append(d.max)
        list_count.append(d.count)
    graph1.add('Minimum', list_min, formatter=formatter)
    graph1.add('Average', list_avg, formatter=formatter)
    graph1.add('Maximum', list_max, formatter=formatter)

    graph2 = pygal.HorizontalBar(height=100 + len(data) * 30, show_legend=False)
    graph2.x_labels = []
    for d in data:
        graph2.x_labels.append(d.newTime)
    graph2.add('Hits', list_count)
    return graph1.render_data_uri(), graph2.render_data_uri()


def get_stacked_bar():
    data = get_reqs_endpoint_day()
    graph = pygal.graph.horizontalstackedbar.HorizontalStackedBar(legend_at_bottom=True, height=100 + len(data) * 7)
    graph.title = 'Number of requests per endpoint per day'
    graph.x_labels = []
    endpoints = []
    for d in data:
        if d.newTime not in graph.x_labels:
            graph.x_labels.append(d.newTime)
        if d.endpoint not in endpoints:
            endpoints.append(d.endpoint)

    for e in endpoints:
        lst = []
        for t in graph.x_labels:
            found = False
            for d in data:
                if e == d.endpoint and t == d.newTime:
                    found = True
                    lst.append(d.cnt)
            if not found:
                lst.append(0)
        graph.add(e, lst)

    return graph.render_data_uri()


def get_dot_charts(end, versions):
    """
    Function that builds two dot charts:
    1. Execution time per version per user
    2. Execution time per version per ip
    :param end: the endpoint
    :param versions: A list with the versions
    :return: graph1, graph2
    """
    user_data = {}
    ip_data = {}
    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        user_data[d] = {}
        for v in versions:
            user_data[d][v] = 0
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        ip_data[d] = {}
        for v in versions:
            ip_data[d][v] = 0

    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.group_by):
        user_data[str(d.group_by)][d.version] = d.average
    for d in get_endpoint_results(end, FunctionCall.ip):
        ip_data[str(d.ip)][d.version] = d.average

    # dot charts
    graph1 = pygal.Dot(x_label_rotation=30, show_legend=False, height=200 + len(user_data) * 40)
    graph1.x_labels = versions

    graph2 = pygal.Dot(x_label_rotation=30, show_legend=False, height=200 + len(ip_data) * 40)
    graph2.x_labels = versions

    # add rows to the charts
    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        data = []
        for v in versions:
            data.append(user_data[d][v])
        graph1.add(d, data, formatter=formatter)
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        data = []
        for v in versions:
            data.append(ip_data[d][v])
        graph2.add(d, data, formatter=formatter)
    return graph1.render_data_uri(), graph2.render_data_uri()


def get_boxplots(end, versions):
    """
        Function that builds two boxplots:
        1. Execution time per version
        2. Execution time per user
        :param end: the endpoint
        :param versions: A list with the versions
        :return: graph1, graph2
        """
    data = []
    for v in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=v)]
        data.append(go.Box(x=values, name=v))

    layout = go.Layout(
        autosize=False,
        width=900,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(title='Version')
    )
    graph1 = plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)

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
    graph2 = plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
    return graph1, graph2


def get_heatmap(end):
    # list of hours: 1:00 - 23:00
    hours = ['0' + str(hour) + ':00' for hour in range(0, 10)] + \
            [str(hour) + ':00' for hour in range(10, 24)]

    data = get_num_requests(end)
    # list of days (format: year-month-day)
    days = [str(d.newTime[:10]) for d in data]
    # remove duplicates and sort the result
    days = sorted(list(set(days)))

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
        autosize=False,
        width=900,
        height=800,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Heatmap of number of requests',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Time')
    )

    trace = go.Heatmap(z=requests_list, x=days, y=hours)
    return plotly.offline.plot(go.Figure(data=[trace], layout=layout), output_type='div', show_link=False)


@blueprint.route('/result/<end>')
@secure
def result(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    versions = [str(c.version) for c in get_endpoint_column(end, FunctionCall.version)]

    # (1) Execution time per hour and (2) Hits per hour
    graph1, graph2 = get_graphs_per_hour(end)

    # (3) Execution time per version per user and (4) Execution time per version per ip
    graph3, graph4 = get_dot_charts(end, versions)

    # (5) Execution time per version and (6) Execution time per user
    graph5, graph6 = get_boxplots(end, versions)

    # (7) Number of requests per hour
    graph7 = get_heatmap(end)

    return render_template('endpoint.html', link=config.link, session=session, rule=rule, url=url,
                           times_data=graph1, hits_data=graph2, dot_chart_user=graph3,
                           dot_chart_ip=graph4, div_versions=graph5, div_users=graph6, div_heatmap=graph7)
