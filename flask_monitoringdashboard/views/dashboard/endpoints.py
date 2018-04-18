import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.database.function_calls import get_endpoints, get_data_per_endpoint
from flask_monitoringdashboard.database.function_calls import get_times


@blueprint.route('/measurements/endpoints')
@secure
def page_boxplot_per_endpoint():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/graph.html', graph=get_boxplot_per_endpoint(), title='Time per endpoint')


def get_boxplot_per_endpoint():
    """
    Creates a graph with the execution times per endpoint
    :return:
    """
    endpoints = get_endpoints()

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
