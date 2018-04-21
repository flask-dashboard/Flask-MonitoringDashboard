import math

import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_endpoint_column, get_endpoint_results, \
    get_all_measurement
from flask_monitoringdashboard.database.count import count_ip
from flask_monitoringdashboard.database.function_calls import get_versions
from flask_monitoringdashboard.database.versions import get_date_first_request
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from .utils import get_endpoint_details, formatter


@blueprint.route('/result/<end>/time_per_version_per_ip', methods=['GET', 'POST'])
@secure
def result_time_per_version_per_ip(end):
    form = get_slider_form(count_ip(end))
    graph = get_time_per_version_per_ip(end, form)
    return render_template('endpoint/time_per_user.html', details=get_endpoint_details(end), graph=graph, form=form)


def get_time_per_version_per_ip(end, form):
    ip_data = {}
    data = [t.execution_time for t in get_all_measurement(end)]
    # compute the average for determining the default size
    average = math.sqrt(sum(data) / len(data)) / 1250
    versions = get_versions(end, limit=form.get_slider_value())

    for d in [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]:
        ip_data[d] = {}
        for version in versions:
            ip_data[d][version] = 0

    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.ip):
        ip_data[str(d.ip)][d.version] = d.average

    db_data = [str(c.ip) for c in get_endpoint_column(end, FunctionCall.ip)]
    trace = []
    for d in db_data:
        data = [ip_data[d][version] for version in versions]

        hover_text = []
        for i in range(len(data)):
            hover_text.append('Version: ' + versions[i] + '<br>Time: ' + formatter(data[i]))

        trace.append(go.Scatter(
            x=["{}<br>{}".format(v, get_date_first_request(v).strftime('%b %d %H:%M')) for v in versions],
            hovertext=hover_text,
            y=[d] * len(versions),
            name=d,
            mode='markers',
            marker=dict(
                color=[get_color(d)] * len(versions),
                size=[math.sqrt(d) for d in data],
                sizeref=average,
                sizemode='area'
            )
        ))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(trace),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Average execution time for every IP-address per version',
        xaxis=dict(
            title='Versions',
            type='category'
        ),
        yaxis=dict(
            type='category',
            title='IP-addresses',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200,
            b=200
        )
    )

    return plotly.offline.plot(go.Figure(data=trace, layout=layout), output_type='div', show_link=False)
