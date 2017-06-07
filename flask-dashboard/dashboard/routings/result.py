import pygal
import math
from flask import session, url_for, render_template
from werkzeug.routing import BuildError

from dashboard import blueprint, config
from dashboard.database import FunctionCall
from dashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule, \
    get_last_accessed_times, get_line_results, get_all_measurement_per_column
from dashboard.database.function_calls import get_times
from dashboard.security import secure

import plotly
import plotly.graph_objs as go


@blueprint.route('/measurements')
@secure
def measurements():
    t = get_times()
    la = get_last_accessed_times()
    return render_template('measurements.html', link=config.link, curr=2, times=t, access=la, session=session)


def formatter(ms):
    """
    formats the ms into seconds and ms
    :param ms: the number of ms
    :return: a string representing the same amount, but now represented in seconds and ms.
    """
    sec = math.floor(ms/1000)
    ms = round(ms % 1000, 2)
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}s and {1}ms'.format(sec, ms)


@blueprint.route('/show-graph/<end>')
@secure
def show_graph(end):

    # bar chart
    data = get_line_results(end)
    times_chart = pygal.HorizontalBar(height=100+len(data)*30)
    times_chart.x_labels = []
    list_avg = []
    list_min = []
    list_max = []
    list_count = []
    for d in data:
        times_chart.x_labels.append(d.newTime)
        list_min.append(d.min)
        list_avg.append(d.avg)
        list_max.append(d.max)
        list_count.append(d.count)
    times_chart.add('Minimum', list_min, formatter=formatter)
    times_chart.add('Average', list_avg, formatter=formatter)
    times_chart.add('Maximum', list_max, formatter=formatter)
    times_data = times_chart.render_data_uri()

    hits_chart = pygal.HorizontalBar(height=100+len(data)*30, show_legend=False)
    hits_chart.x_labels = []
    for d in data:
        hits_chart.x_labels.append(d.newTime)
    hits_chart.add('Hits', list_count)
    hits_data = hits_chart.render_data_uri()

    # get measurements from database
    rule = get_monitor_rule(end)

    versions = [str(c.version) for c in get_endpoint_column(end, FunctionCall.version)]

    # urls that require additional arguments, like /static/<file> cannot be retrieved.
    # This raises a BuildError
    try:
        url = url_for(end)
    except BuildError:
        url = None

    # define the rows
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
    dot_chart_user = pygal.Dot(x_label_rotation=30, show_legend=False, height=200+len(user_data)*40)
    dot_chart_user.x_labels = versions

    dot_chart_ip = pygal.Dot(x_label_rotation=30, show_legend=False, height=200+len(ip_data)*40)
    dot_chart_ip.x_labels = versions

    # add rows to the charts
    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        data = []
        for v in versions:
            data.append(user_data[d][v])
        dot_chart_user.add(d, data, formatter=formatter)
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        data = []
        for v in versions:
            data.append(ip_data[d][v])
        dot_chart_ip.add(d, data, formatter=formatter)

    # boxplot: execution time per versions
    versions = [str(c.version) for c in get_endpoint_column(endpoint=end, column=FunctionCall.version)]

    data = []
    for v in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=v)]
        data.append(go.Box(x=values, name=v))

    layout = go.Layout(
        autosize=False,
        width=1000,
        height=350+40*len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False
    )
    div_versions = plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)

    # boxplot: execution time per versions
    users = [str(c.group_by) for c in get_endpoint_column(endpoint=end, column=FunctionCall.group_by)]

    data = []
    for u in users:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.group_by, value=u)]
        data.append(go.Box(x=values, name=u))

    layout = go.Layout(
        autosize=False,
        width=1000,
        height=350 + 40 * len(users),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False
    )
    div_users = plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)

    return render_template('show-graph.html', link=config.link, session=session, rule=rule, url=url,
                           times_data=times_data, hits_data=hits_data, dot_chart_user=dot_chart_user.render_data_uri(),
                           dot_chart_ip=dot_chart_ip.render_data_uri(), div_versions=div_versions, div_users=div_users)
