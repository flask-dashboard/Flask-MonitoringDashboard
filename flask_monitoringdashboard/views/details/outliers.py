from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details, get_mean_cpu
from flask_monitoringdashboard.database import Outlier, session_scope
from flask_monitoringdashboard.database.count import count_outliers
from flask_monitoringdashboard.database.outlier import get_outliers_sorted, delete_outliers_without_stacktrace, \
    get_outliers_cpus

OUTLIERS_PER_PAGE = 10


@blueprint.route('/result/<end>/outliers')
@secure
def result_outliers(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        delete_outliers_without_stacktrace(db_session)
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        table = get_outliers_sorted(db_session, end, Outlier.execution_time, offset, per_page)
        all_cpus = get_outliers_cpus(db_session, end)
        mean = get_mean_cpu(all_cpus)
        pagination = Pagination(page=page, per_page=per_page, total=count_outliers(db_session, end), format_number=True,
                                css_framework='bootstrap4', format_total=True, record_name='outliers')

    return render_template('fmd_dashboard/outliers.html', details=details, table=table, pagination=pagination, mean=mean)
