import ast

from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.core.utils import get_endpoint_details, simplify
from flask_monitoringdashboard.database import Outlier, session_scope
from flask_monitoringdashboard.database.count import count_outliers
from flask_monitoringdashboard.database.outlier import get_outliers_sorted, delete_outliers_without_stacktrace, \
    get_outliers_cpus
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin

OUTLIERS_PER_PAGE = 10
NUM_DATAPOINTS = 50


@blueprint.route('/endpoint/<end>/outliers')
@secure
def outliers(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        delete_outliers_without_stacktrace(db_session)
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        table = get_outliers_sorted(db_session, end, Outlier.execution_time, offset, per_page)
        for outl in table:
            outl.time = to_local_datetime(outl.time)
        all_cpus = get_outliers_cpus(db_session, end)
        graph = cpu_load_graph(all_cpus)
        pagination = Pagination(page=page, per_page=per_page, total=count_outliers(db_session, end), format_number=True,
                                css_framework='bootstrap4', format_total=True, record_name='outliers')
    return render_template('fmd_dashboard/outliers.html', details=details, table=table, pagination=pagination,
                           title='Outliers for {}'.format(end), graph=graph)


def cpu_load_graph(all_cpus):
    count = 0  # some outliers have no CPU info
    values = []  # list of lists that stores the CPU info
    for cpu in all_cpus:
        if not cpu:
            continue
        x = ast.literal_eval(cpu[0])
        values.append(x)
        count += 1

    simplified = [simplify(x, NUM_DATAPOINTS) for x in zip(*values)]
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
