import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.core.auth import secure, is_admin
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times
from flask_monitoringdashboard.database.function_calls import get_hits, get_median, get_endpoints


@blueprint.route('/measurements/overview')
@secure
def overview():
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    result = []
    for endpoint in get_endpoints():
        result.append({
            'name': endpoint,
            'color': get_color(endpoint),
            'hits-today': get_hits(endpoint, today),
            'hits-week': get_hits(endpoint, week_ago),
            'hits-overall': get_hits(endpoint),
            'median-today': get_median(endpoint, today),
            'median-week': get_median(endpoint, week_ago),
            'median-overall': get_median(endpoint),
            'last-accessed': get_last_accessed_times(endpoint)
        })

    return render_template('dashboard/overview.html', result=result, is_admin=is_admin(),
                           title='Dashboard Overview')
