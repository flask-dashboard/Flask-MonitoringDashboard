from typing import Union
from sqlalchemy.orm import Session
import os
import sys
from flask_monitoringdashboard.core.filter_exceptions import ExceptionFilter
from flask_monitoringdashboard.database import FunctionDefinition
from flask_monitoringdashboard.database.exception_info import (
    delete_exception,
    get_exceptions_with_timestamps,
    get_exceptions_with_timestamps_and_stack_trace_id,
)
from flask_monitoringdashboard.database.stack_trace_snapshot import (
    get_stacklines_from_stack_trace_snapshot_id,
)
from flask_monitoringdashboard.database.function_definition import (
    get_function_definition_from_id,
    get_function_startlineno_and_relativelineno_from_function_definition_id,
)

app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
app_parent_dir = os.path.dirname(app_dir) + os.sep


def get_exception_groups(
    session: Session, offset: int, per_page: int, filter: ExceptionFilter
):
    """
    Gets information about exceptions including timestamps of latest and first occurrence.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param filter: the query parameter filter
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
            "type": exception.type,
            "message": exception.message,
            "endpoint": exception.name,
            "endpoint_id": exception.id,
            "latest_timestamp": exception.latest_timestamp,
            "first_timestamp": exception.first_timestamp,
            "count": exception.count,
        }
        for exception in get_exceptions_with_timestamps(
            session, offset, per_page, filter
        )
    ]


def delete_exceptions_via_stack_trace_snapshot_id(
    session: Session, stack_trace_snapshot_id: int
) -> None:
    """
    Deletes the specified exception
    :param session: session for the database
    :param stack_trace_snapshot_id: stack trace id to be deleted
    :return: None
    """
    delete_exception(session, stack_trace_snapshot_id)


def get_exception_groups_with_details_for_endpoint(
    session: Session, offset: int, per_page: int, endpoint_id: int
):
    """
    Gets detailed information about exceptions on an endpoint (including stack trace).
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: the id of the endpoint
    :return: A list of dicts. Each dict contains:
             - type (str) of the exception
             - message (str) of the exception
             - stack_trace_snapshot_id (int)
             - stack_trace_snapshot (lst of dicts) Each dict contains:
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
            "type": exception.type,
            "message": exception.message,
            "stack_trace_snapshot_id": exception.stack_trace_snapshot_id,
            "stack_trace_snapshot": [
                {
                    "filename": _get_relative_file_path_if_in_app(
                        exceptionStackLine.code.filename
                    ),
                    "line_number": exceptionStackLine.code.line_number,
                    "function_name": exceptionStackLine.code.function_name,
                    "function_definition_id": exceptionStackLine.function_definition_id,
                    "position": exceptionStackLine.position,
                }
                for exceptionStackLine in get_stacklines_from_stack_trace_snapshot_id(
                    session, exception.stack_trace_snapshot_id
                )
            ],
            "latest_timestamp": exception.latest_timestamp,
            "first_timestamp": exception.first_timestamp,
            "count": exception.count,
        }
        for exception in get_exceptions_with_timestamps_and_stack_trace_id(
            session, offset, per_page, endpoint_id
        )
    ]


def get_exception_function_definition(
    session: Session, function_id: int, stack_trace_id: int, position: int
):
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
    result: Union[FunctionDefinition, None] = get_function_definition_from_id(
        session, function_id
    )
    line_numbers = (
        get_function_startlineno_and_relativelineno_from_function_definition_id(
            session, function_id, stack_trace_id, position
        )
    )
    if result is None or line_numbers is None:
        return {}
    file_lineno, relative_lineno = line_numbers
    start_lineno = file_lineno - relative_lineno
    return {
        "start_line_number": start_lineno,
        "function_code": result.function_code,
        "exception_line_number": relative_lineno,
    }


def _get_relative_file_path_if_in_app(file_path: str):
    """
    Returns the relative file path if the file is within the application directory. Otherwise, returns the full file path.
    :param file_path: The full file path to be checked.
    :return: The relative file path if the file is inside the app directory, otherwise the full file path.
    """
    if file_path.startswith(app_parent_dir):
        return file_path[len(app_parent_dir) :]
    return file_path
