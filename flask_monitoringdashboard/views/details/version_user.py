import math

import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_endpoint_column, get_endpoint_results, get_all_measurement
from flask_monitoringdashboard.database.function_calls import get_versions
from flask_monitoringdashboard.core.auth import secure
from .utils import get_endpoint_details, BUBBLE_SIZE_RATIO, get_form, formatter


@blueprint.route('/result/<end>/time_per_version_per_user', methods=['GET', 'POST'])
@secure
def result_time_per_version_per_user(end):
    title = 'Time per version per user for endpoint: {}'.format(end)
    graph, form = get_time_per_version_per_user(end, get_versions(end))
    return render_template('endpoint/time_per_user.html', title=title, details=get_endpoint_details(end),
                           graph=graph, form=form)


def get_time_per_version_per_user(end, versions):
    user_data = {}
    data = [t.execution_time for t in get_all_measurement(end)]
    # compute the average for determining the size of the bubbles in the plot
    average = math.sqrt(sum(data) / len(data)) / BUBBLE_SIZE_RATIO

    for d in [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]:
        user_data[d] = {}
        for v in versions:
            user_data[d][v.version] = 0

    form, selection = get_form(user_data)
    # fill the rows with data
    for d in get_endpoint_results(end, FunctionCall.group_by):
        user_data[str(d.group_by)][d.version] = d.average

    db_data = [str(c.group_by) for c in get_endpoint_column(end, FunctionCall.group_by)]
    trace = []
    for d in db_data:  # iterate through all (unique) ip addresses
        if selection == [] or d in selection:
            data = []
            for version in versions:
                data.append(user_data[d][version.version])

            hover_text = []
            for i in range(len(data)):
                hover_text.append('Version: ' + versions[i].version + '<br>Time: ' + formatter(data[i]))

            trace.append(go.Scatter(
                x=["{0}<br>{1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M")) for v in versions],
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
        title='Average execution time for every user per version',
        xaxis=dict(
            title='Versions',
            type='category'
        ),
        yaxis=dict(
            type='category',
            title='Users',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200,
            b=200
        )
    )

    return plotly.offline.plot(go.Figure(data=trace, layout=layout), output_type='div', show_link=False), form
