import ast

from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.core.utils import get_endpoint_details, simplify
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_outliers
from flask_monitoringdashboard.database.outlier import get_outliers_sorted, get_outliers_cpus

DATA_POINTS = 50


@blueprint.route('/endpoint/<endpoint_id>/outliers')
@secure
def outliers(endpoint_id):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, endpoint_id)
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        table = get_outliers_sorted(db_session, endpoint_id, offset, per_page)
        for outlier in table:
            outlier.request.time_requested = to_local_datetime(outlier.request.time_requested)
        all_cpus = get_outliers_cpus(db_session, endpoint_id)
        graph = cpu_load_graph(all_cpus)

        total = count_outliers(db_session, endpoint_id)
        pagination = Pagination(page=page, per_page=per_page, total=total, format_number=True,
                                css_framework='bootstrap4', format_total=True, record_name='outliers')
    return render_template('fmd_dashboard/outliers.html', details=details, table=table, pagination=pagination,
                           title='Outliers for {}'.format(details['endpoint']), graph=graph)


def cpu_load_graph(all_cpus):
    count = 0  # some outliers have no CPU info
    values = []  # list of lists that stores the CPU info
    for cpu in all_cpus:
        if not cpu:
            continue
        x = ast.literal_eval(cpu)
        values.append(x)
        count += 1

    simplified = [simplify(x, DATA_POINTS) for x in zip(*values)]
    cores = []
    for i in range(len(simplified)):
        cores.append('CPU core %d:' % i)

    data = [boxplot(name=cores[idx], values=simplified[idx], marker={'color': get_color(core)})
            for idx, core in enumerate(cores)]

    layout = get_layout(
        height=150 + 40 * len(cores),
        xaxis={'title': 'CPU loads (%)'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin(l=100, t=0)
    )
    return get_figure(layout=layout, data=data)
