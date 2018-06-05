from collections import defaultdict

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.profiler.util import order_histogram
from flask_monitoringdashboard.core.profiler.util.groupedStackLine import GroupedStackLine
from flask_monitoringdashboard.core.profiler.util.pathHash import PathHash
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.stack_line import get_grouped_profiled_requests

SEPARATOR = ' / '


@blueprint.route('/endpoint/<endpoint_id>/grouped-profiler')
@secure
def grouped_profiler(endpoint_id):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, endpoint_id)
        end = details['endpoint']
        requests = get_grouped_profiled_requests(db_session, endpoint_id)
        db_session.expunge_all()
    total_execution_time = sum([r.duration for r in requests])
    num_requests = len(requests) if len(requests) > 0 else 1

    histogram = defaultdict(list)  # path -> [list of values]
    path_hash = PathHash()
    for r in requests:
        for index in range(len(r.stack_lines)):
            line = r.stack_lines[index]
            key = path_hash.get_stacklines_path(r.stack_lines, index), line.code.code
            histogram[key].append(line.duration)

    table = []
    for key, duration_list in order_histogram(histogram.items()):
        table.append(GroupedStackLine(indent=path_hash.get_indent(key[0]), code=key[1], hits=len(duration_list),
                                      sum=sum(duration_list), total=total_execution_time))

    for index in range(len(table)):
        table[index].compute_body(index, table)

    return render_template('fmd_dashboard/profiler_grouped.html', details=details, table=table,
                           title='Grouped Profiler results for {}'.format(end))
