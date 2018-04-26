from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.database import Outlier
from flask_monitoringdashboard.database.outlier import get_outliers_sorted, delete_outliers_without_stacktrace
from flask_monitoringdashboard.database.count import count_outliers
from flask_monitoringdashboard.core.utils import get_endpoint_details

OUTLIERS_PER_PAGE = 10


@blueprint.route('/result/<end>/outliers')
@secure
def result_outliers(end):
    delete_outliers_without_stacktrace()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    table = get_outliers_sorted(end, Outlier.execution_time, offset, per_page)
    pagination = Pagination(page=page, per_page=per_page, total=count_outliers(end), format_number=True,
                            css_framework='bootstrap4', format_total=True, record_name='outliers')

    return render_template('dashboard/outliers.html', details=get_endpoint_details(end), table=table,
                           pagination=pagination)
