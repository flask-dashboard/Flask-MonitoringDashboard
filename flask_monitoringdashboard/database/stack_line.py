"""
Contains all functions that access an StackLine object.
"""

from sqlalchemy import desc, distinct
from sqlalchemy.orm import joinedload

from flask_monitoringdashboard.database import StackLine, Request
from flask_monitoringdashboard.database.code_line import get_code_line


def add_stack_line(session, request_id, position, indent, duration, code_line):
    """
    Adds a StackLine to the database (and possibly a CodeLine)
    :param session: Session for the database
    :param request_id: id of the request
    :param position: position of the StackLine
    :param indent: indent-value
    :param duration: duration of this line (in ms)
    :param code_line: quadruple that consists of: (filename, line_number, function_name, code)
    """
    fn, ln, name, code = code_line
    db_code_line = get_code_line(session, fn, ln, name, code)
    session.add(
        StackLine(
            request_id=request_id,
            position=position,
            indent=indent,
            code_id=db_code_line.id,
            duration=duration,
        )
    )


def get_profiled_requests(session, endpoint_id, offset, per_page):
    """
    Gets the requests of an endpoint sorted by request time, together with the stack lines.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list with tuples. Each tuple consists first of a Request-object, and the second part
    of the tuple is a list of StackLine-objects.
    """
    result = (
        session.query(Request)
        .filter(Request.endpoint_id == endpoint_id)
        .options(joinedload(Request.stack_lines).joinedload(StackLine.code))
        .filter(Request.stack_lines.any())
        .order_by(desc(Request.time_requested))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    session.expunge_all()
    return result


def get_grouped_profiled_requests(session, endpoint_id):
    """
    Gets the grouped stack lines of all requests of an endpoint.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :return: A list with tuples. Each tuple consists first of a Request-object, and the second part
    of the tuple is a list of StackLine-objects.
    """
    t = (
        session.query(distinct(StackLine.request_id).label('id'))
        .filter(Request.endpoint_id == endpoint_id)
        .join(Request.stack_lines)
        .order_by(StackLine.request_id.desc())
        .limit(100)
        .subquery('t')
    )
    # Limit the number of results by 100, otherwise the profiler gets too large
    # and the page doesn't load anymore. We show the most recent 100 requests.
    result = (
        session.query(Request)
        .join(Request.stack_lines)
        .filter(Request.id == t.c.id)
        .order_by(desc(Request.id))
        .options(joinedload(Request.stack_lines).joinedload(StackLine.code))
        .all()
    )
    session.expunge_all()
    return result
