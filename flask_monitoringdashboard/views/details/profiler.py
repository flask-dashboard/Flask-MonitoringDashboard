from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_profiled_requests
from flask_monitoringdashboard.database.execution_path_line import get_profiled_requests

OUTLIERS_PER_PAGE = 10


@blueprint.route('/endpoint/<end>/profiler')
@secure
def profiler(end):
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        table = get_profiled_requests(db_session, end, offset, per_page)

        pagination = Pagination(page=page, per_page=per_page, total=count_profiled_requests(db_session, end),
                                format_number=True, css_framework='bootstrap4', format_total=True,
                                record_name='profiled requests')
    return render_template('fmd_dashboard/profiler.html', details=details, table=table, pagination=pagination,
                           title='Profiler results for {}'.format(end))
