import datetime

import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database.endpoint import get_line_results
from flask_monitoringdashboard.core.auth import secure
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/time_per_hour')
@secure
def result_time_per_hour(end):
    title = 'Time per hour for endpoint: {}'.format(end)
    return render_template('endpoint/plotly.html', title=title, details=get_endpoint_details(end),
                           graph=get_time_per_hour(end))


def get_time_per_hour(end):
    data = get_line_results(end)

    # Find the last date which contains data
    max_time = max([d.newTime for d in data])
    max_date = datetime.datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
    max_date += datetime.timedelta(minutes=30)

    trace1 = go.Bar(
        x=[d.newTime for d in data],
        y=[d.min for d in data],
        name='Minimum'
    )

    trace2 = go.Bar(
        x=[d.newTime for d in data],
        y=[d.avg for d in data],
        name='Average'
    )

    trace3 = go.Bar(
        x=[d.newTime for d in data],
        y=[d.max for d in data],
        name='Maximum'
    )

    graph = [trace3, trace2, trace1]

    layout = go.Layout(
        autosize=True,
        height=600,
        title='Execution time (minimum, average and maximum) per hour',
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=True,
        barmode='overlay',
        xaxis=go.XAxis(
            title='Date',
            range=[max_date - datetime.timedelta(days=2), max_date]
        ),
        yaxis=go.YAxis(
            title='Execution time (ms)'
        )
    )
    return plotly.offline.plot(go.Figure(data=graph, layout=layout), output_type='div', show_link=False)

