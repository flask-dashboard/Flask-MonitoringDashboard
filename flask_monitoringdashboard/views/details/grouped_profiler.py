from functools import reduce

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.execution_path_line import get_grouped_profiled_requests

OUTLIERS_PER_PAGE = 10


def get_body(index, lines):
    """
    Return the lines (as a list) that belong to the line given in the index
    :param index: integer, between 0 and length(lines)
    :param lines: all lines belonging to a certain request. Every element in this list is an ExecutionPathLine-obj.
    :return: an empty list if the index doesn't belong to a function. If the list is not empty, it denotes the body of
    the given line (by the index).
    """
    body = []
    indent = lines[index].get('indent')
    index += 1
    while index < len(lines) and lines[index].get('indent') > indent:
        body.append(index)
        index += 1
    return body


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
        data = get_grouped_profiled_requests(db_session, end)
    lines = [lines for _, lines in data]
    lines = reduce(lambda x, y: x + y, lines)

    histogram = {}
    for line in lines:
        key = (line.indent, line.line_text)
        if key in histogram:
            histogram[key].append(line.value)
        else:
            histogram[key] = [line.value]

    total = max([sum(s) for s in histogram.values()])
    table = []
    index = 0
    for key, values in histogram.items():
        indent, line_text = key
        table.append({
            'index': index,
            'indent': indent,
            'code': line_text,
            'hits': len(values),
            'average': sum(values) / len(values),
            'percentage': sum(values) / total
        })
        index += 1

    total_time = [request.execution_time for request, _ in data]
    average_time = sum(total_time) / len(total_time)
    return render_template('fmd_dashboard/profiler_grouped.html', details=details, table=table, get_body=get_body,
                           average_time=average_time, title='Grouped Profiler results for {}'.format(end))
