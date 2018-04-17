import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.core.auth import secure, is_admin
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times
from flask_monitoringdashboard.database.function_calls import get_times, get_hits, get_average


@blueprint.route('/measurements/overview')
@secure
def overview():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)

    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    return render_template('dashboard/dashboard-base.html', times=get_times(), colors=colors,
                           access=get_last_accessed_times(), is_admin=is_admin(), hits_last_days=get_hits(week_ago),
                           hits_today=get_hits(today), average_last_days=get_average(week_ago),
                           average_today=get_average(today), title='Dashboard Overview')
