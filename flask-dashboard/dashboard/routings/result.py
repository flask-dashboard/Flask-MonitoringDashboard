import pygal
from collections import Counter
from flask import session, url_for
from werkzeug.routing import BuildError

from dashboard import user_app, link, env
from dashboard.database import FunctionCall
from dashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_monitor_rule
from dashboard.database.endpoint import get_all_measurement, get_last_accessed_times, get_line_results
from dashboard.database.function_calls import get_times
from dashboard.security import secure


@user_app.route('/' + link + '/measurements')
@secure
def render_dashboard_results():
    t = get_times()
    la = get_last_accessed_times()
    return env.get_template('measurements.html').\
        render(times=t, access=la, link=link, session=session)


@user_app.route('/' + link + '/show-graph/<string:endpoint>')
@secure
def dashboard_show_graph(endpoint):
    # create line diagram
    data = get_line_results(endpoint)
    line_chart = pygal.HorizontalLine(height=100+len(data)*30, show_minor_x_labels=False)
    line_chart.title = 'Execution time per hour'
    line_chart.x_labels = []
    list_avg = []
    list_min = []
    list_max = []
    list_count = []
    for d in data:
        line_chart.x_labels.append(d.newTime)
        list_avg.append(d.avg)
        list_min.append(d.min)
        list_max.append(d.max)
        list_count.append(d.count)
    print(line_chart.x_labels)
    line_chart.add('Maximum', list_max)
    line_chart.add('Average', list_avg)
    line_chart.add('Minimum', list_min)
    line_chart.add('Hits', list_count, secondary=True)
    chart_data = line_chart.render_data_uri()

    for d in data:
        print(d)

    # get measurements from data and create histogram
    result = get_all_measurement(endpoint)
    rule = get_monitor_rule(endpoint)
    execution_times = []
    for data in result:
        execution_times.append(round(data.execution_time))
    hist = Counter(execution_times)

    # Create tuple list
    tuple_list = []
    for data in hist:
        tuple_list.append((hist[data], data, data+1))

    # Create graph
    graph = pygal.Histogram()
    graph.title = 'Histogram of execution times'
    graph.add("Execution time", tuple_list)
    graph_data = graph.render_data_uri()

    # Fill table with data from db
    cols = get_endpoint_column(endpoint, FunctionCall.version)
    rows = get_endpoint_column(endpoint, FunctionCall.group_by)
    rows2 = get_endpoint_column(endpoint, FunctionCall.ip)
    table_data = {}
    table_data2 = {}
    for c in cols:
        table_data[c.version] = {}
        table_data2[c.version] = {}

    for d in get_endpoint_results(endpoint, FunctionCall.group_by):
        table_data[d.version][d.group_by] = d

    for d in get_endpoint_results(endpoint, FunctionCall.ip):
        table_data2[d.version][d.ip] = d

    # urls that require additional arguments, like /static/<file> cannot be retrieved.
    # This raises a BuildError
    try:
        url = url_for(endpoint)
    except BuildError:
        url = None

    return env.get_template('show-graph.html').\
        render(link=link, session=session, rule=rule, graph_data=graph_data, rows=rows, rows2=rows2, cols=cols,
               table_data=table_data, table_data2=table_data2, url=url, chart_data=chart_data)
