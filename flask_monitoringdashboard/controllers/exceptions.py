from flask_monitoringdashboard.database import FunctionDefinition
from flask_monitoringdashboard.database.exception_info import delete_exception, get_exceptions_with_timestamps, get_exceptions_with_timestamps_and_stacktrace_id
from flask_monitoringdashboard.database.full_stack_trace import get_stacklines_from_full_stacktrace_id
from flask_monitoringdashboard.database.function_definition import get_function_definition_from_id, get_function_startlineno_and_relativelineno_from_function_definition_id

def get_exceptions_with_timestamp(session, offset, per_page):
    """
    Gets information about exceptions including timestamps of latest and first occurence. 
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - endpoint name (str)
             - endpoint_id (int)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    
    return [
        {
            'type': exception.type, 
            'message': exception.message, 
            'endpoint': exception.name,
            'endpoint_id': exception.id,
            'latest_timestamp': exception.latest_timestamp,
            'first_timestamp': exception.first_timestamp,
            'count': exception.count
        }
        for exception in get_exceptions_with_timestamps(session, offset, per_page)
    ]

def delete_exceptions_via_full_stack_trace_id(session, full_stack_trace_id: int) -> None:
    """
    Deltes the specified exception
    :param session: session for the database
    :param full_stack_trace: stack trace id to be deleted
    :return: None
    """
    delete_exception(session, full_stack_trace_id)

def get_detailed_exception_info(session, offset, per_page, endpoint_id):
    """
    Gets detailed information about exceptions on an endpoint (including stack trace).
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: the id of the endpoint
    :return: A list of dicts. Each dict contains:
             - type (str) of the exception
             - message (str) of the exception
             - full_stack_trace_id (int)
             - full_stacktrace (lst of dicts) Each dict contains:
                - code (str)
                - filename (str)
                - line_number (int)
                - function_name (str)
                - function_definition_id (int)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    return [
        {
            'type': exception.type, 
            'message': exception.message, 
            'full_stack_trace_id': exception.full_stack_trace_id,
            'full_stacktrace': [ 
                {
                    'filename': exceptionStackLine.code.filename,
                    'line_number': exceptionStackLine.code.line_number,
                    'function_name': exceptionStackLine.code.function_name,
                    'function_definition_id': exceptionStackLine.function_definition_id
                }
                for exceptionStackLine in get_stacklines_from_full_stacktrace_id(session, exception.full_stack_trace_id)],
            'latest_timestamp': exception.latest_timestamp,
            'first_timestamp': exception.first_timestamp,
            'count': exception.count
        }
        for exception in get_exceptions_with_timestamps_and_stacktrace_id(session, offset, per_page, endpoint_id)]

def get_exception_function_definition(session, function_id, stack_trace_id):
    """
    Retrieves the source code of the function where an exception occurred, the starting line number of the function in the source file, and the relative line number of the exception.
    :param session: session for the database
    :param function_id: the id of the function
    :param stack_trace_id: the id of the stack trace
    :return: a dict containing:
             - start_line_number (int)
             - code (str)
             - exception_line_number (int)
    """
    result : FunctionDefinition | None = get_function_definition_from_id(session, function_id)
    file_lineno, relative_lineno = get_function_startlineno_and_relativelineno_from_function_definition_id(session, function_id, stack_trace_id)
    if result is None or file_lineno is None or relative_lineno is None: return []
    startlineno = file_lineno - relative_lineno
    return {
            'start_line_number': startlineno,
            'function_code': result.function_code,
            'exception_line_number': relative_lineno
        }
