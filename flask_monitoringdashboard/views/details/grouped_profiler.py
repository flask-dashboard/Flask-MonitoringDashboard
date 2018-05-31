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


@blueprint.route('/endpoint/<end>/grouped-profiler')
@secure
def grouped_profiler(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        data = get_grouped_profiled_requests(db_session, end)
    lines = [lines for _, lines in data]
    requests = [requests for requests, _ in data]
    total_execution_time = 0
    for r in requests:
        total_execution_time += r.execution_time
    lines = reduce(lambda x, y: x + y, lines)

    histogram = {}
    for line in lines:
        key = (line.indent, line.line_text)
        if key in histogram:
            histogram[key].append((line.value, line.line_number))
        else:
            histogram[key] = [(line.value, line.line_number)]

    total = max([sum(s[0]) for s in histogram.values()])
    table = []
    index = 0
    for key, values in histogram.items():
        total_line_hits = 0
        sum_line_number = 0
        for v in values:
            total_line_hits += v[0]
            sum_line_number += v[1]

        indent, line_text = key
        table.append({
            'index': index,
            'indent': indent,
            'code': line_text,
            'hits': len(values),
            'average': total_execution_time / len(requests),
            'percentage': total_line_hits / (total * len(values)),
            'avg_ln': sum_line_number / len(values)
        })
        index += 1

    total_execution_time = [request.execution_time for request, _ in data]
    average_time = sum(total_execution_time) / len(total_execution_time)
    table = sorted(table, key=lambda row: row.get('avg_ln'))
    return render_template('fmd_dashboard/profiler_grouped.html', details=details, table=table, get_body=get_body,
                           average_time=average_time, title='Grouped Profiler results for {}'.format(end))
