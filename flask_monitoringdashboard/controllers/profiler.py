from collections import defaultdict

import numpy

from flask_monitoringdashboard.core.profiler.util import PathHash
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database import row2dict
from flask_monitoringdashboard.database.stack_line import (
    get_profiled_requests,
    get_grouped_profiled_requests,
)


def get_profiler_table(session, endpoint_id, offset, per_page):
    """
    :param session: session for the database
    :param endpoint_id: endpoint to filter on
    :param offset: number of items that are skipped
    :param per_page: number of items that are returned (at most)
    """
    table = get_profiled_requests(session, endpoint_id, offset, per_page)

    for idx, row in enumerate(table):
        row.time_requested = to_local_datetime(row.time_requested)
        table[idx] = row2dict(row)
        stack_lines = []
        for line in row.stack_lines:
            obj = row2dict(line)
            obj['code'] = row2dict(line.code)
            stack_lines.append(obj)
        table[idx]['stack_lines'] = stack_lines
    return table


def get_grouped_profiler(session, endpoint_id):
    """
    :param session: session for the database
    :param endpoint_id: endpoint to filter on
    :return:
    """
    requests = get_grouped_profiled_requests(session, endpoint_id)
    session.expunge_all()

    histogram = defaultdict(list)  # path -> [list of values]
    path_hash = PathHash()

    for r in requests:
        for index, stack_line in enumerate(r.stack_lines):
            key = path_hash.get_stacklines_path(r.stack_lines, index)
            histogram[key].append(stack_line.duration)

    table = []
    for key, duration_list in sorted(histogram.items(), key=lambda row: row[0]):
        table.append(
            {
                'indent': path_hash.get_indent(key) - 1,
                'code': path_hash.get_code(key),
                'hits': len(duration_list),
                'duration': sum(duration_list),
                'std': numpy.std(duration_list),
                'total_hits': len(requests),
            }
        )
    return table
