import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.auth import secure, is_admin
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times
from flask_monitoringdashboard.database.function_calls import get_median, get_endpoints
from flask_monitoringdashboard.database.count import count_requests


@blueprint.route('/measurements/overview')
@secure
def overview():
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    result = []
    with session_scope() as db_session:
        for endpoint in get_endpoints(db_session):
            result.append({
                'name': endpoint,
                'color': get_color(endpoint),
                'hits-today': count_requests(db_session, endpoint, FunctionCall.time > today),
                'hits-week': count_requests(db_session, endpoint, FunctionCall.time > week_ago),
                'hits-overall': count_requests(db_session, endpoint),
                'median-today': get_median(db_session, endpoint, FunctionCall.time > today),
                'median-week': get_median(db_session, endpoint, FunctionCall.time > week_ago),
                'median-overall': get_median(db_session, endpoint),
                'last-accessed': get_last_accessed_times(db_session, endpoint)
            })

    return render_template('fmd_dashboard/overview.html', result=result, is_admin=is_admin(),
                           title='Dashboard Overview')
