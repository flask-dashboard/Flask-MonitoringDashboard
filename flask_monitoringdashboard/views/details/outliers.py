import ast

from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import Outlier, session_scope
from flask_monitoringdashboard.database.count import count_outliers
from flask_monitoringdashboard.database.outlier import get_outliers_sorted, delete_outliers_without_stacktrace, get_outliers_cpus

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

    return render_template('dashboard/outliers.html', details=details, table=table, pagination=pagination, mean=mean)


def get_mean_cpu(cpu_percentages):
    """
    Returns a list containing mean CPU percentages per core for all given CPU percentages.
    :param cpu_percentages: list of CPU percentages
    """
    if not cpu_percentages:
        return None

    count = 0 # some outliers have no CPU info
    values = [] # list of lists that stores the CPU info

    for cpu in cpu_percentages:
        if not cpu:
            continue
        x = ast.literal_eval(cpu[0])
        values.append(x)
        count += 1

    sums = [sum(x) for x in zip(*values)]
    means = list(map(lambda x: round(x/count), sums))
    return means
