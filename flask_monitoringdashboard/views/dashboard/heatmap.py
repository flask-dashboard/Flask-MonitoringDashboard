import datetime

import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.database.endpoint import get_num_requests


@blueprint.route('/measurements/heatmap', methods=['GET', 'POST'])
@secure
def heatmap():
    form = get_daterange_form()
    return render_template('dashboard/graph.html', form=form, graph=get_heatmap(form), title='Heatmap')


def get_heatmap(form, end=None):
    """
    Return HTML code for generating a Heatmap.
    :param form: A SelectDateRangeForm, which is used to filter the selection
    :param end: optionally, filter the data on a specific endpoint
    :return: HTML code with the graph
    """
    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]

    delta = form.end_date.data - form.start_date.data
    days = [form.start_date.data + datetime.timedelta(days=i) for i in range(delta.days + 1)]

    # create empty 2D-list: [hour][day]
    heatmap_data = []
    for i in range(len(hours)):
        heatmap_data.append([])
        [heatmap_data[i].append(0) for _ in days]

    # add data from database to heatmap_data
    for d in get_num_requests(end, form.start_date.data, form.end_date.data):
        parsed_time = datetime.datetime.strptime(d.newTime, '%Y-%m-%d %H:%M:%S')
        day_index = (parsed_time - datetime.datetime.combine(form.start_date.data, datetime.time(0, 0, 0, 0))).days
        hour_index = int(parsed_time.strftime('%H'))
        heatmap_data[hour_index][day_index] = d.count

    layout = go.Layout(
        autosize=True,
        height=800,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Heatmap of number of requests',
        xaxis=go.XAxis(range=[(form.start_date.data - datetime.timedelta(days=1, hours=6)).
                       strftime('%Y-%m-%d 12:00:00'), form.end_date.data.strftime('%Y-%m-%d 12:00:00')],
                       title='Date'),
        yaxis=dict(title='Time', autorange='reversed')
    )
    trace = go.Heatmap(z=heatmap_data, x=days, y=hours)
    return plotly.offline.plot(go.Figure(data=[trace], layout=layout), output_type='div', show_link=False)
