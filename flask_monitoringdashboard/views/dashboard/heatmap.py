import datetime

import plotly
import plotly.graph_objs as go
from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database.endpoint import get_num_requests
from flask_monitoringdashboard.database.function_calls import get_times
from flask_monitoringdashboard.core.auth import secure


@blueprint.route('/measurements/heatmap')
@secure
def heatmap():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/dashboard.html', link=config.link, curr=2, session=session, index=1,
                           graph=get_heatmap(end=None), title='Heatmap')


def get_heatmap(end):
    # list of hours: 1:00 - 23:00
    hours = ['0' + str(hour) + ':00' for hour in range(0, 10)] + \
            [str(hour) + ':00' for hour in range(10, 24)]

    data = get_num_requests(end)
    # list of days (format: year-month-day)
    days = [str(d.newTime[:10]) for d in data]
    # remove duplicates and sort the result
    days = sorted(list(set(days)))

    if len(data) == 0:
        return None

    first_day = max(datetime.datetime.strptime(days[0], '%Y-%m-%d'),
                    datetime.datetime.now() - datetime.timedelta(days=30))
    first_day -= datetime.timedelta(hours=12)
    last_day = datetime.datetime.strptime(days[len(days) - 1], '%Y-%m-%d') + datetime.timedelta(hours=12)

    # create empty 2D-dictionary with the keys: [hour][day]
    requests = {}
    for hour in hours:
        requests_day = {}
        for day in days:
            requests_day[day] = 0
        requests[hour] = requests_day

    # add data to the dictionary
    for d in data:
        day = str(d.newTime[:10])
        hour = str(d.newTime[11:16])
        requests[hour][day] = d.count

    # create a 2D-list out of the dictionary
    requests_list = []
    for hour in hours:
        day_list = []
        for day in days:
            day_list.append(requests[hour][day])
        requests_list.append(day_list)

    layout = go.Layout(
        autosize=True,
        height=800,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Heatmap of number of requests',
        xaxis=go.XAxis(range=[first_day, last_day],
                       title='Date'),
        yaxis=dict(title='Time', autorange='reversed')
    )

    trace = go.Heatmap(z=requests_list, x=days, y=hours)
    return plotly.offline.plot(go.Figure(data=[trace], layout=layout), output_type='div', show_link=False)
