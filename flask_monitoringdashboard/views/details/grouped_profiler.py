from collections import defaultdict

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.profiler.util.groupedStackLine import GroupedStackLine
from flask_monitoringdashboard.core.profiler.util.pathHash import PathHash
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.stack_line import get_grouped_profiled_requests


@blueprint.route('/endpoint/<endpoint_id>/grouped-profiler')
@secure
def grouped_profiler(endpoint_id):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, endpoint_id)
        requests = get_grouped_profiled_requests(db_session, endpoint_id)
        db_session.expunge_all()
    total_duration = sum([r.duration for r in requests])
    histogram = defaultdict(list)  # path -> [list of values]
    path_hash = PathHash()

    for r in requests:
        for index, stack_line in enumerate(r.stack_lines):
            key = path_hash.get_stacklines_path(r.stack_lines, index)
            histogram[key].append(stack_line.duration)

    table = []
    for key, duration_list in sorted(histogram.items(), key=lambda row: row[0]):
        table.append(GroupedStackLine(indent=path_hash.get_indent(key) - 1, code=path_hash.get_code(key),
                                      values=duration_list, total_sum=total_duration, total_hits=len(requests)))
    for index, item in enumerate(table):
        table[index].compute_body(index, table)

    return render_template('fmd_dashboard/profiler_grouped.html', details=details, table=table,
                           title='Grouped Profiler results for {}'.format(details['endpoint']))
