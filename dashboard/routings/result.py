import pygal
import math
from flask import session, url_for, render_template
from werkzeug.routing import BuildError

from dashboard import blueprint, config
from dashboard.database import FunctionCall
from dashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule, \
    get_last_accessed_times, get_line_results, get_all_measurement_per_column, get_num_requests, \
    get_endpoint_column_user_sorted
from dashboard.database.function_calls import get_times, get_data_per_version, get_versions, get_reqs_endpoint_day, \
    get_endpoints, get_data_per_endpoint
from dashboard.security import secure

import plotly
import plotly.graph_objs as go

import datetime


@blueprint.route('/measurements')
@secure
def measurements():
    return render_template('measurements.html', link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session,
                           heatmap=get_heatmap(end=None), etpv=get_boxplot_per_version(), rpepd=get_stacked_bar(),
                           etpe=get_boxplot_per_endpoint())


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
        autosize=False,
        width=900,
        height=350 + 40 * len(endpoints),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every endpoint',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(tickangle=-45)
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

    data1 = [trace1, trace2, trace3]

    layout = go.Layout(
        autosize=False,
        width=900,
        height=600,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=True,
        barmode='group',
        xaxis=go.XAxis(range=[datetime.datetime.now() - datetime.timedelta(days=2), datetime.datetime.now()])
    )
    graph1 = plotly.offline.plot(go.Figure(data=data1, layout=layout), output_type='div', show_link=False)

    data2 = [go.Bar(
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
    graph2 = plotly.offline.plot(go.Figure(data=data2, layout=layout), output_type='div', show_link=False)

    return graph1, graph2


def get_stacked_bar():
    data = get_reqs_endpoint_day()
    graph = pygal.graph.horizontalstackedbar.HorizontalStackedBar(height=100 + len(data) * 7)
    graph.title = 'Number of requests per endpoint per day'
    graph.x_labels = []
    endpoints = []
    for d in data:
        if d.newTime not in graph.x_labels:
            graph.x_labels.append(d.newTime)
        if d.endpoint not in endpoints:
            endpoints.append(d.endpoint)

    graph.x_labels.sort(reverse=True)
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
            user_data[d][v.version] = 0
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        ip_data[d] = {}
        for v in versions:
            ip_data[d][v.version] = 0

    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.group_by):
        user_data[str(d.group_by)][d.version] = d.average
    for d in get_endpoint_results(end, FunctionCall.ip):
        ip_data[str(d.ip)][d.version] = d.average

    # dot charts
    graph1 = pygal.Dot(x_label_rotation=30, show_legend=False, height=200 + len(user_data) * 40)
    graph1.x_labels = ["{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions]

    graph2 = pygal.Dot(x_label_rotation=30, show_legend=False, height=200 + len(ip_data) * 40)
    graph2.x_labels = ["{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions]

    # add rows to the charts
    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        data = []
        for v in versions:
            data.append(user_data[d][v.version])
        graph1.add(d, data, formatter=formatter)
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        data = []
        for v in versions:
            data.append(ip_data[d][v.version])
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
        autosize=False,
        width=900,
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


@blueprint.route('/result/<end>')
@secure
def result(end):
    rule = get_monitor_rule(end)
    url = get_url(end)
    versions = get_versions(end)

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
