"""
Contains all functions that access an StackLine object.
"""
from flask_monitoringdashboard.database import StackLine, StackLineQuery
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
    StackLineQuery(session).create_stack_line(StackLine(
        request_id=request_id,
        position=position,
        indent=indent,
        code_id=db_code_line.id,
        duration=duration,
    ))


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
    return StackLineQuery(session).get_profiled_requests(endpoint_id, offset, per_page)


def get_grouped_profiled_requests(session, endpoint_id):
    """
    Gets the grouped stack lines of all requests of an endpoint.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :return: A list with tuples. Each tuple consists first of a Request-object, and the second part
    of the tuple is a list of StackLine-objects.
    """
    return StackLineQuery(session).get_grouped_profiled_requests(endpoint_id)
