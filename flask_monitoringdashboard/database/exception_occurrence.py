"""
Contains all functions that access an ExceptionOccurrence object.
"""

from types import TracebackType
from typing import Union
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from flask_monitoringdashboard.core.exceptions.stack_frame_parsing import (
    get_function_definition_from_frame,
)
from flask_monitoringdashboard.core.exceptions.stack_trace_hashing import (
    hash_stack_trace,
)

from flask_monitoringdashboard.database import (
    ExceptionOccurrence,
    Request,
    Endpoint,
    ExceptionType,
    ExceptionMessage,
)
from flask_monitoringdashboard.core.database_pruning import (
    delete_entries_unreferenced_by_exception_occurrence,
)
from flask_monitoringdashboard.database.exception_frame import add_exception_frame
from flask_monitoringdashboard.database.exception_message import add_exception_message
from flask_monitoringdashboard.database.exception_stack_line import (
    add_exception_stack_line,
)
from flask_monitoringdashboard.database.exception_type import add_exception_type
from flask_monitoringdashboard.database.file_path import add_file_path
from flask_monitoringdashboard.database.function_definition import (
    add_function_definition,
)
from flask_monitoringdashboard.database.function_location import add_function_location
from flask_monitoringdashboard.database.stack_trace_snapshot import (
    get_stack_trace_by_hash,
    add_stack_trace_snapshot,
)


def add_exception_occurrence(
    session: Session,
    request_id: int,
    trace_id: int,
    exception_type_id: int,
    exception_msg_id: int,
    is_user_captured: bool,
):
    """
    Add a new ExceptionOccurrence record.
    :return: The saved ExceptionOccurrence record
    """
    exception_occurrence = ExceptionOccurrence(
        request_id=request_id,
        exception_type_id=exception_type_id,
        exception_msg_id=exception_msg_id,
        stack_trace_snapshot_id=trace_id,
        is_user_captured=is_user_captured,
    )
    session.add(exception_occurrence)
    session.commit()
    return exception_occurrence


def count_grouped_exceptions(session: Session):
    """
    Count the number of different kinds of exceptions grouped by endpoint and stack trace snapshot.
    :param session: session for the database
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(Endpoint.name, ExceptionOccurrence.stack_trace_snapshot_id)
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .group_by(Endpoint.name, ExceptionOccurrence.stack_trace_snapshot_id)
        .count()
    )


def count_endpoint_grouped_exceptions(session: Session, endpoint_id: int):
    """
    Count the number of different kinds of exceptions on an endpoint grouped by stack trace snapshot.
    :param session: session for the database
    :param endpoint_id: filter exceptions on this endpoint id
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionOccurrence.stack_trace_snapshot_id)
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .filter(Endpoint.id == endpoint_id)
        .group_by(ExceptionOccurrence.stack_trace_snapshot_id)
        .count()
    )


def get_exceptions_with_timestamps(session: Session, offset: int, per_page: int):
    """
    Gets the information about exceptions grouped by endpoint and stack trace snapshot and sorted by latest request time.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - endpoint name (str)
             - endpoint id (int)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
        session.query(
            ExceptionType.type,
            ExceptionMessage.message,
            Endpoint.name,
            Endpoint.id,
            func.max(Request.time_requested).label("latest_timestamp"),
            func.min(Request.time_requested).label("first_timestamp"),
            func.count(ExceptionOccurrence.request_id).label("count"),
        )
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .join(ExceptionType, ExceptionOccurrence.exception_type)
        .join(ExceptionMessage, ExceptionOccurrence.exception_msg)
        .group_by(
            Endpoint.name,
            Endpoint.id,
            ExceptionType.type,
            ExceptionMessage.message,
            ExceptionOccurrence.stack_trace_snapshot_id
        )
        .order_by(desc("latest_timestamp"))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return result


def delete_exception_group(session: Session, stack_trace_snapshot_id: int) -> None:
    """
    Deletes a group of exceptions based on the stack trace id
    :param session: session for the database
    :param stack_trace_snapshot_id: the stack trace id
    :return: None
    """
    _ = (
        session.query(ExceptionOccurrence)
        .filter(ExceptionOccurrence.stack_trace_snapshot_id == stack_trace_snapshot_id)
        .delete()
    )
    delete_entries_unreferenced_by_exception_occurrence(session)
    session.commit()


def get_exceptions_with_timestamps_and_stack_trace_id(
    session: Session, offset: int, per_page: int, endpoint_id: int
):
    """
    Gets the information about exceptions on an endpoint grouped by stack trace snapshot and sorted by latest request time.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: filter exceptions on this endpoint id
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - stack_trace_snapshot_id (int) for the exceptions
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
        session.query(
            ExceptionType.type,
            ExceptionMessage.message,
            ExceptionOccurrence.stack_trace_snapshot_id,
            func.max(Request.time_requested).label("latest_timestamp"),
            func.min(Request.time_requested).label("first_timestamp"),
            func.count(ExceptionOccurrence.request_id).label("count"),
        )
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .join(ExceptionType, ExceptionOccurrence.exception_type)
        .join(ExceptionMessage, ExceptionOccurrence.exception_msg)
        .filter(Endpoint.id == endpoint_id)
        .group_by(
            ExceptionType.type,
            ExceptionMessage.message,
            ExceptionOccurrence.stack_trace_snapshot_id
        )
        .order_by(desc("latest_timestamp"))
        .offset(offset)
        .limit(per_page)
        .all()
    )

    return result


def get_exception_group_page_number_by_endpoint(
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
    subquery = (
        session.query(
            ExceptionOccurrence.stack_trace_snapshot_id,
            (func.row_number().over(order_by=desc(func.max(Request.time_requested))) - 1).label("row_index")
        )
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .join(ExceptionType, ExceptionOccurrence.exception_type)
        .join(ExceptionMessage, ExceptionOccurrence.exception_msg)
        .filter(Endpoint.id == endpoint_id)
        .group_by(
            ExceptionType.type,
            ExceptionMessage.message,
            ExceptionOccurrence.stack_trace_snapshot_id
        )
        .subquery()
    )
    result = (
        session.query(
            (subquery.c.row_index // per_page + 1).label("page")
        )
        .filter(subquery.c.stack_trace_snapshot_id == stack_trace_snapshot_id)
        .scalar()
    )

    return int(result)


def check_if_stack_trace_exists(session: Session, exc: BaseException, tb: Union[TracebackType, None]) -> bool:
    """
    Check if a stack_trace_snapshot already exists in the database.
    """

    hashed_trace = hash_stack_trace(exc, tb)
    stacktrace = get_stack_trace_by_hash(session, hashed_trace)
    return stacktrace is not None


def save_exception_occurence_to_db(
    request_id: int,
    session: Session,
    exc: BaseException,
    typ: type[BaseException],
    tb: Union[TracebackType, None],
    is_user_captured: bool,
):
    """
    Save exception occurence to DB
    """
    hashed_trace = hash_stack_trace(exc, tb)
    existing_trace = get_stack_trace_by_hash(session, hashed_trace)

    if existing_trace:
        is_new_group = False
        trace_id = int(existing_trace.id)
    else:
        is_new_group = True
        trace_id = add_stack_trace_snapshot(session, hashed_trace)
        idx = 0
        while tb:
            # iterate over traceback-type objects
            # i.e. the object representation of the following traceback
            # Traceback (most recent call last):
            #   File "example.py", line 9, in <module>
            #     calculate()
            #   File "example.py", line 6, in calculate
            #     return divide(10, 0)
            #   File "example.py", line 2, in divide
            #     return a / b
            # ZeroDivisionError: division by zero
            f_def = get_function_definition_from_frame(tb.tb_frame)
            function_id = add_function_definition(session, f_def)
            file_path = add_file_path(session, tb.tb_frame.f_code.co_filename)
            f_location_id = add_function_location(
                session,
                file_path,
                function_id,
                tb.tb_frame.f_code.co_firstlineno,
            )
            frame_id = add_exception_frame(session, f_location_id, tb.tb_lineno)
            add_exception_stack_line(
                session,
                trace_id,
                frame_id,
                idx,
            )
            tb = tb.tb_next
            idx += 1

    exc_msg_id = add_exception_message(session, str(exc))
    exc_type_id = add_exception_type(session, typ.__name__)
    exception_occurrence = add_exception_occurrence(
        session, request_id, trace_id, exc_type_id, exc_msg_id, is_user_captured
    )
    return exception_occurrence.request.endpoint_id, trace_id, is_new_group
