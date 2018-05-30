from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.execution_path_line import get_grouped_profiled_requests

OUTLIERS_PER_PAGE = 10


def get_path(lines, index):
    """
    Returns a list that corresponds to the path to the root.
    For example, if lines consists of the following code:
    0.  f():
    1.      g():
    2.          time.sleep(1)
    3.      time.sleep(1)
    get_path(lines, 0) ==> ['f():']
    get_path(lines, 3) ==> ['f():', 'time.sleep(1)']

    :param lines: List of ExecutionPathLine-objects
    :param index: integer in range 0 .. len(lines)
    :return: A list with strings
    """
    path = []
    while index >= 0:
        path.append(lines[index].line_text)
        current_indent = lines[index].indent
        while index >= 0 and lines[index].indent != current_indent - 1:
            index -= 1
    return ' / '.join(reversed(path))


@blueprint.route('/endpoint/<end>/grouped-profiler')
@secure
def grouped_profiler(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        table = get_grouped_profiled_requests(db_session, end)
    histogram = {}
    total_time = []
    for request, lines in table:
        for index in range(len(lines)):
            path = get_path(lines, index)
            if path in histogram:
                histogram[path].append(lines[index].value)
            else:
                histogram[path] = [lines[index].value]
        total_time.append(request.execution_time)
    total = max([sum(s) for s in histogram.values()])
    table = []
    index = 0
    for code, values in histogram.items():
        table.append({
            'index': index,
            'code': code,
            'hits': len(values),
            'average': sum(values) / len(values),
            'percentage': sum(values) / total
        })
        index += 1
    average_time = sum(total_time) / len(total_time)
    return render_template('fmd_dashboard/profiler_grouped.html', details=details, table=table, average_time=average_time,
                           title='Grouped Profiler results for {}'.format(end))
