
"""
This file contains all unit tests of function definition in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/function_definition.py')
"""
from flask_monitoringdashboard.database import FunctionDefinition
from flask_monitoringdashboard.database.function_definition import add_function_definition, get_function_definition_from_id, get_function_startlineno_and_relativelineno_from_function_definition_id

def test_add_function_definition(session, function_definition):
    function_definition_id = add_function_definition(session, function_definition)
    f_def = session.query(FunctionDefinition).filter(FunctionDefinition.id == function_definition_id).one()
    assert f_def.function_code == function_definition.function_code
    assert f_def.function_hash == function_definition.function_hash

def test_add_existing_function_definition(session, function_definition):
    function_definition_id = add_function_definition(session, function_definition)
    function_definition_count = session.query(FunctionDefinition).count()
    function_definition_id_2 = add_function_definition(session, function_definition)
    assert function_definition_count == session.query(FunctionDefinition).count()
    assert function_definition_id == function_definition_id_2

def test_get_function_definition_from_id(session, function_definition):
    f_def = get_function_definition_from_id(session, function_definition.id)
    assert f_def.id == function_definition.id
    assert f_def.function_code == function_definition.function_code
    assert f_def.function_hash == function_definition.function_hash

def test_get_function_definition_from_invalid_id(session):
    f_def = get_function_definition_from_id(session, -1)
    assert f_def is None

def test_get_function_startlineno_and_relativelineno_from_function_definition_id(session, exception_stack_line):
    start_line_number, relative_line_number = get_function_startlineno_and_relativelineno_from_function_definition_id(session, exception_stack_line.function_definition_id, exception_stack_line.full_stack_trace_id)
    assert start_line_number == exception_stack_line.code.line_number
    assert relative_line_number == exception_stack_line.relative_line_number

def test_get_function_startlineno_and_relativelineno_from_invalid_id(session):
    result = get_function_startlineno_and_relativelineno_from_function_definition_id(session, -1, -1)
    assert result is None
