import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column
from flask_monitoringdashboard.database.function_calls import get_versions
from flask_monitoringdashboard.core.auth import secure
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/time_per_version')
@secure
def result_time_per_version(end):
    title = 'Time per version for endpoint: {}'.format(end)
    return render_template('endpoint/plotly.html', title=title, details=get_endpoint_details(end),
                           graph=get_time_per_version(end, get_versions(end)))


def get_time_per_version(end, versions):
    data = []
    for v in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=v.version)]

        data.append(go.Box(
            x=values,
            marker=dict(
                color=get_color(end)
            ),
            name="{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M"))))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(
            title='Version',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200
        )
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
