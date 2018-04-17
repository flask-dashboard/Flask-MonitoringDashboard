import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.database.function_calls import get_times, get_reqs_endpoint_day


@blueprint.route('/measurements/requests')
@secure
def page_number_of_requests_per_endpoint():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/dashboard.html', graph=get_stacked_bar(), title='Requests per endpoint')


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
