from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot, get_margin
from flask_monitoringdashboard.database.function_calls import get_endpoints, get_data_per_endpoint


@blueprint.route('/measurements/endpoints')
@secure
def page_boxplot_per_endpoint():
    return render_template('dashboard/graph.html', graph=get_boxplot_per_endpoint())


def get_boxplot_per_endpoint():
    """
    Creates a graph with the execution times per endpoint
    :return:
    """
    endpoints = get_endpoints()

    data = []
    for endpoint in endpoints:
        values = [c.execution_time for c in get_data_per_endpoint(endpoint)]
        if len(values) > 0:
            data.append(boxplot(values, name=endpoint))

    if len(data) == 0:
        return None

    layout = get_layout(
        height=350 + 40 * len(endpoints),
        title='Execution time for every endpoint',
        xaxis=dict(title='Execution time (ms)'),
        margin=get_margin()
    )
    return get_figure(layout, data)
