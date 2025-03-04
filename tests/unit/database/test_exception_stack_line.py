
"""
This file contains all unit tests of exception stack line in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_stack_line.py')
"""
from flask_monitoringdashboard.database import ExceptionStackLine
from flask_monitoringdashboard.database.exception_stack_line import add_exception_stack_line

def test_add_exception_stack_line(session, full_stack_trace, function_definition, code_line):
    assert session.query(ExceptionStackLine).filter(ExceptionStackLine.full_stack_trace_id == full_stack_trace.id).one_or_none() is None
    add_exception_stack_line(session, full_stack_trace_id=full_stack_trace.id, position=0, code_line=code_line, function_defintion_id=function_definition.id, relative_lineno=1)
    session.commit()
    assert session.query(ExceptionStackLine).filter(ExceptionStackLine.full_stack_trace_id == full_stack_trace.id).one()