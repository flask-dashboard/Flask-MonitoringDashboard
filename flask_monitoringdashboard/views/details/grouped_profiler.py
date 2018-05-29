from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.execution_path_line import get_grouped_profiled_requests
from flask_monitoringdashboard.views.details.profiler import get_body

OUTLIERS_PER_PAGE = 10


@blueprint.route('/endpoint/<end>/grouped-profiler')
@secure
def grouped_profiler(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        table = get_grouped_profiled_requests(db_session, end)
    return render_template('fmd_dashboard/profiler.html', details=details, table=table,
                           title='Grouped Profiler results for {}'.format(end), get_body=get_body)
