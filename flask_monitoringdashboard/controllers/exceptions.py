from sqlalchemy.orm import Session
import os
import sys
from flask_monitoringdashboard.database.exception_occurrence import (
    delete_exception_group,
    get_exceptions_with_timestamps,
    get_exceptions_with_timestamps_and_stack_trace_id,
    get_exception_group_page_number_by_endpoint,
)
from flask_monitoringdashboard.database.stack_trace_snapshot import (
    get_stacklines_from_stack_trace_snapshot_id,
)
from flask_monitoringdashboard.database.function_definition import (
    get_function_definition_code_from_id,
)

app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
app_parent_dir = os.path.dirname(app_dir) + os.sep


def get_exception_groups(session: Session, offset: int, per_page: int):
    """
    Gets information about exceptions including timestamps of latest and first occurrence.
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
            "type": exception.type,
            "message": exception.message,
            "endpoint": exception.name,
            "endpoint_id": exception.id,
            "latest_timestamp": exception.latest_timestamp,
            "first_timestamp": exception.first_timestamp,
            "count": exception.count,
        }
        for exception in get_exceptions_with_timestamps(session, offset, per_page)
    ]


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
             - stack_trace_snapshot (list of dicts) Each dict contains:
                - position (int)
                - full_file_path (str)
                - file_path (str)
                - function_name (str)
                - function_definition_id (int)
                - function_start_line_number (int)
                - line_number (int)
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
                    "position": exceptionStackLine.position,
                    "full_file_path": exceptionStackLine.path,
                    "file_path": _get_relative_file_path_if_in_app(
                        exceptionStackLine.path
                    ),
                    "function_definition_id": exceptionStackLine.function_definition_id,
                    "function_name": exceptionStackLine.name,
                    "function_start_line_number": exceptionStackLine.function_start_line_number,
                    "line_number": exceptionStackLine.line_number,
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


def get_exception_group_page_number_for_endpoint(
        session: Session, per_page: int, endpoint_id: int, stack_trace_snapshot_id: int
):
    """
    Get the page number of an exception group that has occurred for a specific endpoint
    :param session: session for the database
    :param per_page: number of items per page
    :param endpoint_id: the id of the endpoint
    :param stack_trace_snapshot_id: the id of the stacktrace snapshot
    :return: The page number of the exception group (int)
    """
    return get_exception_group_page_number_by_endpoint(session, per_page, endpoint_id, stack_trace_snapshot_id)


def get_function_definition_code(session: Session, function_definition_id: int):
    """
    Retrieves the source code of the function where an exception occurred, the starting line number of the function in the source file, and the relative line number of the exception.
    :param session: session for the database
    :param exception_frame_id: the id of the exception frame
    :return: entire code of the function (str)
    """

    return get_function_definition_code_from_id(session, function_definition_id)


def _get_relative_file_path_if_in_app(file_path: str):
    """
    Returns the relative file path if the file is within the application directory. Otherwise, returns the full file path.
    :param file_path: The full file path to be checked.
    :return: The relative file path if the file is inside the app directory, otherwise the full file path.
    """
    if file_path.startswith(app_parent_dir):
        return file_path[len(app_parent_dir) :]
    return file_path
