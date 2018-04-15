import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column, get_endpoint_column_user_sorted
from flask_monitoringdashboard.auth import secure
from .utils import get_endpoint_details, get_form


@blueprint.route('/result/<end>/time_per_user', methods=['GET', 'POST'])
@secure
def result_time_per_user(end):
    title = 'Time per user for endpoint: {}'.format(end)
    graph, form = get_time_per_user(end)
    return render_template('endpoint/time_per_user.html', title=title, details=get_endpoint_details(end),
                           graph=graph, form=form)


def get_time_per_user(end):
    users = [str(c.group_by) for c in get_endpoint_column_user_sorted(endpoint=end, column=FunctionCall.group_by)]
    form, selection = get_form(users)
    data = []
    for user in users:
        if selection == [] or user in selection:
            values = [str(c.execution_time) for c in
                      get_all_measurement_per_column(endpoint=end, column=FunctionCall.group_by, value=user)]
            data.append(go.Box(
                x=values,
                marker=dict(
                    color=get_color(user)
                ),
                name='{0}  -'.format(user)))
    data.reverse()
    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(data),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every user',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(title='User')
    )
    graph = plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
    return graph, form
