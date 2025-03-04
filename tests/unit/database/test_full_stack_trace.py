
"""
This file contains all unit tests of full stack trace in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/full_stack_trace.py')
"""
import pytest
from flask_monitoringdashboard.database import FullStackTrace
from flask_monitoringdashboard.database.full_stack_trace import get_stack_trace_by_hash, add_full_stack_trace, get_stacklines_from_full_stacktrace_id

def test_add_full_stack_trace(session):
    full_stack_trace_count = session.query(FullStackTrace).count()
    stack_trace_hash = "test_hash"
    full_stack_trace_id = add_full_stack_trace(session, stack_trace_hash)
    f_stack_trace = session.query(FullStackTrace).filter(FullStackTrace.stack_trace_hash == stack_trace_hash).one()
    assert full_stack_trace_id == f_stack_trace.id
    assert full_stack_trace_count + 1 == session.query(FullStackTrace).count()

def test_add_existing_full_stack_trace(session, full_stack_trace):
    full_stack_trace_id = add_full_stack_trace(session, full_stack_trace.stack_trace_hash)
    full_stack_trace_count = session.query(FullStackTrace).count()
    full_stack_trace_id_2 = add_full_stack_trace(session, full_stack_trace.stack_trace_hash)
    assert full_stack_trace_count == session.query(FullStackTrace).count()
    assert full_stack_trace_id == full_stack_trace_id_2

def test_get_stack_trace_by_hash(session, full_stack_trace):
    f_stack_trace = get_stack_trace_by_hash(session, full_stack_trace.stack_trace_hash)
    assert f_stack_trace.id == full_stack_trace.id

def test_get_stack_trace_by_invalid_hash(session):
    f_stack_trace = get_stack_trace_by_hash(session, 'invalid')
    assert f_stack_trace is None

def test_get_stacklines_from_full_stacktrace_id(session, exception_stack_line):
    stacklines = get_stacklines_from_full_stacktrace_id(session, exception_stack_line.full_stack_trace_id)
    assert len(stacklines) == 1
    assert stacklines[0].full_stack_trace_id == exception_stack_line.full_stack_trace_id
    assert stacklines[0].code_id == exception_stack_line.code_id
    assert stacklines[0].position == exception_stack_line.position
    assert stacklines[0].function_definition_id == exception_stack_line.function_definition_id
    assert stacklines[0].relative_line_number == exception_stack_line.relative_line_number