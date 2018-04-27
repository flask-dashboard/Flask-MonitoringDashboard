import datetime

import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, heatmap as plot_heatmap
from flask_monitoringdashboard.database.endpoint import get_num_requests


TITLE = 'Heatmap of the number of requests'


@blueprint.route('/measurements/heatmap', methods=['GET', 'POST'])
@secure
def heatmap():
    form = get_daterange_form()
    return render_template('dashboard/graph.html', form=form, graph=get_heatmap(form), title=TITLE)


def get_heatmap(form, end=None):
    """
    Return HTML string for generating a Heatmap.
    :param form: A SelectDateRangeForm, which is used to filter the selection
    :param end: optionally, filter the data on a specific endpoint
    :return: HTML code with the graph
    """
    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]
    days = form.get_days()

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

    title = TITLE
    if end:
        title += ' for endpoint: {}'.format(end)

    layout = get_layout(
        title=title,
        xaxis=go.XAxis(range=[(form.start_date.data - datetime.timedelta(days=1, hours=6)).
                       strftime('%Y-%m-%d 12:00:00'), form.end_date.data.strftime('%Y-%m-%d 12:00:00')],
                       title='Date'),
        yaxis={'title': 'Time', 'autorange': 'reversed'}
    )
    return get_figure(layout, [plot_heatmap(x=days, y=hours, z=heatmap_data)])
