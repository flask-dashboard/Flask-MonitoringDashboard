from flask import render_template
from flask_paginate import get_page_args, Pagination

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_profiled_requests
from flask_monitoringdashboard.database.execution_path_line import get_profiled_requests

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
    indent = lines[index].indent
    index += 1
    while index < len(lines) and lines[index].indent > indent:
        body.append(index)
        index += 1
    return body


@blueprint.route('/endpoint/<end>/profiler')
@secure
def profiler(end):
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        table = get_profiled_requests(db_session, end, offset, per_page)

        pagination = Pagination(page=page, per_page=per_page, total=count_profiled_requests(db_session, end),
                                format_number=True, css_framework='bootstrap4', format_total=True,
                                record_name='profiled requests')
    return render_template('fmd_dashboard/profiler.html', details=details, table=table, pagination=pagination,
                           title='Profiler results for {}'.format(end), get_body=get_body)
