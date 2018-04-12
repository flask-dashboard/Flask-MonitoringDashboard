import datetime

from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times
from flask_monitoringdashboard.database.function_calls import get_times, get_hits, get_average
from flask_monitoringdashboard.security import secure, is_admin


@blueprint.route('/measurements/overview')
@secure
def overview():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)

    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    return render_template('dashboard/dashboard-base.html', link=config.link, curr=2, times=get_times(),
                           colors=colors, access=get_last_accessed_times(), session=session, index=0,
                           is_admin=is_admin(), hits_last_days=get_hits(week_ago), hits_today=get_hits(today),
                           average_last_days=get_average(week_ago), average_today=get_average(today),
                           title='Dashboard Overview')
