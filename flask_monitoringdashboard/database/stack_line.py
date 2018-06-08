"""
Contains all functions that access an StackLine object.
"""
from sqlalchemy import desc, distinct
from sqlalchemy.orm import joinedload

from flask_monitoringdashboard.database import StackLine, Request
from flask_monitoringdashboard.database.code_line import get_code_line


def add_stack_line(db_session, request_id, position, indent, duration, code_line):
    """
    Adds a StackLine to the database (and possible a CodeLine)
    :param db_session: Session for the database
    :param request_id: id of the request
    :param position: position of the StackLine
    :param indent: indent-value
    :param duration: duration of this line (in ms)
    :param code_line: quadruple that consists of: (filename, line_number, function_name, code)
    """
    fn, ln, name, code = code_line
    db_code_line = get_code_line(db_session, fn, ln, name, code)
    db_session.add(StackLine(request_id=request_id, position=position, indent=indent, code_id=db_code_line.id,
                             duration=duration))


def get_profiled_requests(db_session, endpoint_id, offset, per_page):
    """
        :param db_session: session for the database
        :param endpoint_id: filter profiled requests on this endpoint
        :param offset: number of items to skip
        :param per_page: number of items to return
        :return: A list with tuples. Each tuple consists first of a Request-object, and the second part of the tuple
            is a list of StackLine-objects.
    """
    t = db_session.query(distinct(StackLine.request_id).label('id')). \
        filter(Request.endpoint_id == endpoint_id). \
        join(Request.stack_lines). \
        order_by(desc(Request.id)). \
        offset(offset).limit(per_page).subquery('t')

    result = db_session.query(Request). \
        join(Request.stack_lines).\
        filter(Request.id == t.c.id).\
        order_by(desc(Request.id)).\
        options(joinedload(Request.stack_lines).joinedload(StackLine.code)).all()
    db_session.expunge_all()
    return result


def get_grouped_profiled_requests(db_session, endpoint_id):
    """
        :param db_session: session for the database
        :param endpoint_id: filter profiled requests on this endpoint
        :return: A list with tuples. Each tuple consists first of a Request-object, and the second part of the tuple
            is a list of StackLine-objects.
    """
    t = db_session.query(distinct(StackLine.request_id).label('id')). \
        filter(Request.endpoint_id == endpoint_id). \
        join(Request.stack_lines).subquery('t')

    result = db_session.query(Request). \
        join(Request.stack_lines). \
        filter(Request.id == t.c.id). \
        order_by(desc(Request.id)). \
        options(joinedload(Request.stack_lines).joinedload(StackLine.code)).all()
    db_session.expunge_all()
    return result
