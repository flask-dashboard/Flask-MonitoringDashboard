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


@blueprint.route('/measurements/<int:index>')
@secure
def measurements(index):
    """
    Returns a page with one of the 4 graphs below:
    TODO: rewrite graph at index==1 to plotly, such that function can be simplified
    :param index:
    :return:
    """

    # returns a page with the number of requests per endpoint
    if index == 1:
        page = 'measurements/measurements_pygal.html'
        graph = get_stacked_bar()

    # returns a page with the execution times per version
    elif index == 2:
        page = 'measurements/measurements_plotly.html'
        graph = get_boxplot_per_version()

    # returns a page with the execution time per endpoint
    elif index == 3:
        page = 'measurements/measurements_plotly.html'
        graph = get_boxplot_per_endpoint()

    # default: return a page with a heatmap of number of requests
    else:
        index = 0
        page = 'measurements/measurements_plotly.html'
        graph = get_heatmap(end=None)

    return render_template(page, link=config.link, curr=2, times=get_times(),
                           access=get_last_accessed_times(), session=session, index=index, graph=graph)


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
