from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_profiled_requests
from flask_monitoringdashboard.database.stack_line import get_profiled_requests


def get_body(index, stack_lines):
    """
    Return the lines (as a list) that belong to the line given in the index
    :param index: integer, between 0 and length(lines)
    :param stack_lines: all lines belonging to a certain request. Every element in this list is an StackLine-obj.
    :return: an empty list if the index doesn't belong to a function. If the list is not empty, it denotes the body of
    the given line (by the index).
    """
    body = []
    indent = stack_lines[index].indent
    index += 1
    while index < len(stack_lines) and stack_lines[index].indent > indent:
        body.append(index)
        index += 1
    return body


@blueprint.route('/endpoint/<endpoint_id>/profiler')
@secure
def profiler(endpoint_id):
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, endpoint_id)
        requests = get_profiled_requests(db_session, endpoint_id, offset, per_page)

        total = count_profiled_requests(db_session, endpoint_id)
    pagination = Pagination(page=page, per_page=per_page, total=total, format_number=True,
                            css_framework='bootstrap4', format_total=True, record_name='profiled requests')

    body = {}  # dict with the request.id as a key, and the values is a list for every stack_line.
    for request in requests:
        request.time_requested = to_local_datetime(request.time_requested)
        body[request.id] = [get_body(index, request.stack_lines) for index, _ in enumerate(request.stack_lines)]

    return render_template('fmd_dashboard/profiler.html', details=details, requests=requests, pagination=pagination,
                           title='Profiler results for {}'.format(details['endpoint']), body=body)
