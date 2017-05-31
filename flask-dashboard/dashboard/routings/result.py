import pygal
from flask import session, url_for, render_template
from werkzeug.routing import BuildError

from dashboard import blueprint, config
from dashboard.database import FunctionCall
from dashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule
from dashboard.database.endpoint import get_last_accessed_times, get_line_results
from dashboard.database.function_calls import get_times
from dashboard.security import secure


@blueprint.route('/measurements')
@secure
def measurements():
    t = get_times()
    la = get_last_accessed_times()
    return render_template('measurements.html', times=t, access=la, link=config.link, session=session)


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
    times_chart.add('Minimum', list_min, formatter=lambda x: '%.2f ms' % x)
    times_chart.add('Average', list_avg, formatter=lambda x: '%.2f ms' % x)
    times_chart.add('Maximum', list_max, formatter=lambda x: '%.2f ms' % x)
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
        dot_chart_user.add(d, data, formatter=lambda x: '%.2f ms' % x)
    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        data = []
        for v in versions:
            data.append(ip_data[d][v])
        dot_chart_ip.add(d, data, formatter=lambda x: '%.2f ms' % x)

    return render_template('show-graph.html', link=config.link, session=session, rule=rule, url=url,
                           times_data=times_data, hits_data=hits_data, dot_chart_user=dot_chart_user.render_data_uri(),
                           dot_chart_ip=dot_chart_ip.render_data_uri())
