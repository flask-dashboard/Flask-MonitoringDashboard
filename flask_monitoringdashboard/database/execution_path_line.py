"""
Contains all functions that access an ExecutionPathLine object.
"""
from sqlalchemy import desc, func

from flask_monitoringdashboard.database import ExecutionPathLine, Request


def add_execution_path_line(db_session, request_id, line_number, indent, line_text, value):
    """ Add an execution path line to the database. """
    db_session.add(ExecutionPathLine(request_id=request_id, line_number=line_number, indent=indent,
                                     line_text=line_text, value=value))


def get_profiled_requests(db_session, endpoint, offset, per_page):
    """
        :param db_session: session for the database
        :param endpoint: filter profiled requests on this endpoint
        :param offset: number of items to skip
        :param per_page: number of items to return
        :return: A list with tuples.
            Each tuple consists first of a Request-object, and the second part of the tuple is a list of
            ExecutionPathLine-objects.
        request.
        """
    # TODO: replace request_id by request-obj
    request_ids = db_session.query(func.distinct(Request.id)). \
        join(ExecutionPathLine, Request.id == ExecutionPathLine.request_id). \
        filter(Request.endpoint == endpoint).order_by(desc(Request.id)).offset(offset).limit(per_page).all()

    data = []
    for request_id in request_ids:
        data.append(
            (request_id, db_session.query(ExecutionPathLine).filter(ExecutionPathLine.request_id == request_id[0]).
             order_by(ExecutionPathLine.line_number).all()))
    db_session.expunge_all()
    return data
