import datetime

import numpy
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, heatmap as plot_heatmap
from flask_monitoringdashboard.core.info_box import get_plot_info
from flask_monitoringdashboard.core.timezone import to_utc_datetime, to_local_datetime
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_num_requests

TITLE = 'Hourly API Utilization'

AXES_INFO = '''The X-axis presents a number of days. The Y-axis presents every hour of 
the day.'''

CONTENT_INFO = '''The color of the cell presents the number of requests that the application received 
in a single hour. The darker the cell, the more requests it has processed. This information can be used 
to validate on which moment of the day the Flask application processes to most requests.'''


@blueprint.route('/hourly_load', methods=['GET', 'POST'])
@secure
def hourly_load():
    form = get_daterange_form()
    return render_template('fmd_dashboard/graph.html', form=form, graph=hourly_load_graph(form), title=TITLE,
                           information=get_plot_info(AXES_INFO, CONTENT_INFO))


def hourly_load_graph(form, endpoint_id=None):
    """
    Return HTML string for generating a Heatmap.
    :param form: A SelectDateRangeForm, which is used to filter the selection
    :param endpoint_id: optionally, filter the data on a specific endpoint
    :return: HTML code with the graph
    """
    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]
    days = form.get_days()

    # create empty 2D-list: [hour][day]
    heatmap_data = numpy.zeros((len(hours), len(days)))

    # add data from database to heatmap_data
    start_datetime = to_utc_datetime(datetime.datetime.combine(form.start_date.data, datetime.time(0, 0, 0, 0)))
    end_datetime = to_utc_datetime(datetime.datetime.combine(form.end_date.data, datetime.time(23, 59, 59)))

    with session_scope() as db_session:
        for time, count in get_num_requests(db_session, endpoint_id, start_datetime, end_datetime):
            parsed_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            day_index = (parsed_time - start_datetime).days
            hour_index = int(to_local_datetime(parsed_time).strftime('%H'))
            heatmap_data[hour_index][day_index] = count

    start_datetime = to_local_datetime(start_datetime - datetime.timedelta(days=1)).strftime('%Y-%m-%d 12:00:00')
    end_datetime = to_local_datetime(form.end_date.data).strftime('%Y-%m-%d 12:00:00')

    layout = get_layout(
        xaxis=go.XAxis(range=[start_datetime, end_datetime])
    )
    return get_figure(layout, [plot_heatmap(x=days, y=hours, z=heatmap_data)])
