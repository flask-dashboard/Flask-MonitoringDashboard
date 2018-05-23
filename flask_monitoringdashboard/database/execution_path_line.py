"""
Contains all functions that access an ExecutionPathLine object.
"""

from flask_monitoringdashboard.database import ExecutionPathLine


def add_execution_path_line(db_session, request_id, line_number, indent, line_text, value):
    """ Add a measurement to the database. """
    db_session.add(ExecutionPathLine(request_id=request_id, line_number=line_number, indent=indent,
                                     line_text=line_text, value=value))
