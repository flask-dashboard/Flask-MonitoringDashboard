import datetime

import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.database.endpoint import get_line_results
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/hits_per_hour')
@secure
def result_hits_per_hour(end):
    return render_template('endpoint/plotly.html', details=get_endpoint_details(end), graph=get_hits_per_hour(end))


def get_hits_per_hour(end):
    data = get_line_results(end)

    # Find the last date which contains data
    max_time = max([d.newTime for d in data])
    max_date = datetime.datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
    max_date += datetime.timedelta(minutes=30)

    graph = [go.Bar(
        x=[d.newTime for d in data],
        y=[d.count for d in data],
        marker=dict(color=get_color(end))
    )]

    layout = go.Layout(
        autosize=True,
        height=600,
        title='Number of hits per hour',
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        xaxis=go.XAxis(
            title='Date',
            range=[max_date - datetime.timedelta(days=2), max_date]
        ),
        yaxis=go.YAxis(title='Hits')
    )
    return plotly.offline.plot(go.Figure(data=graph, layout=layout), output_type='div', show_link=False)
