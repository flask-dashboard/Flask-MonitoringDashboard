import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure, is_admin
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count_group import count_requests_group, get_value
from flask_monitoringdashboard.database.data_grouped import get_endpoint_data_grouped
from flask_monitoringdashboard.database.endpoint import get_last_accessed_times
from flask_monitoringdashboard.database.function_calls import get_endpoints


@blueprint.route('/overview')
@secure
def overview():
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    now_local = to_local_datetime(datetime.datetime.utcnow())
    today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = to_utc_datetime(today_local)

    result = []
    with session_scope() as db_session:
        from numpy import median

        hits_today = count_requests_group(db_session, FunctionCall.time > today_utc)
        hits_week = count_requests_group(db_session, FunctionCall.time > week_ago)
        hits = count_requests_group(db_session)

        median_today = get_endpoint_data_grouped(db_session, median, FunctionCall.time > today_utc)
        median_week = get_endpoint_data_grouped(db_session, median, FunctionCall.time > week_ago)
        median = get_endpoint_data_grouped(db_session, median)
        access_times = get_last_accessed_times(db_session)

        for endpoint in get_endpoints(db_session):
            result.append({
                'name': endpoint,
                'color': get_color(endpoint),
                'hits-today': get_value(hits_today, endpoint),
                'hits-week': get_value(hits_week, endpoint),
                'hits-overall': get_value(hits, endpoint),
                'median-today': get_value(median_today, endpoint),
                'median-week': get_value(median_week, endpoint),
                'median-overall': get_value(median, endpoint),
                'last-accessed': get_value(access_times, endpoint, default=None)
            })

    return render_template('fmd_dashboard/overview.html', result=result, is_admin=is_admin(),
                           title='Dashboard Overview')
