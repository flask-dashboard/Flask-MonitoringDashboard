"""
Contains all functions that access an ExceptionInfo object.
"""
from os import walk
from sqlalchemy import func, desc
from flask_monitoringdashboard.database import ExceptionInfo, ExceptionStackLine, FullStackTrace, Request, Endpoint
from flask_monitoringdashboard.core.database_pruning import delete_unreferenced_entries
def get_exception_info(session, request_id: int):
    """
    Retrieve an ExceptionInfo record by request_id.
    """
    return session.query(ExceptionInfo).filter_by(request_id=request_id).first()
    
def add_exception_info(session, request_id: int, trace_id: int, exception_type_id: str, exception_msg_id: str):
    """
    Add a new ExceptionInfo record.
    """
    exception_info = ExceptionInfo(
        request_id=request_id,
        exception_type_id=exception_type_id,
        exception_msg_id=exception_msg_id,
        full_stack_trace_id=trace_id
    )
    session.add(exception_info)
    session.commit()
    return exception_info

def count_grouped_exceptions(session):
    """
    Count the number of different kinds of exceptions grouped by endpoint and full stack trace.
    :param session: session for the database
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionInfo.request_id)
        .join(Request, ExceptionInfo.request)                  # Join Request via relationship
        .join(Endpoint, Request.endpoint)                      # Join Endpoint via Request's relationship
        .group_by(Endpoint.name, ExceptionInfo.full_stack_trace_id)
        .count()
    )

def count_endpoint_grouped_exceptions(session, endpoint_id):
    """
    Count the number of different kinds of exceptions on an endpoint grouped by full stack trace.
    :param session: session for the database
    :param endpoint_id: filter exceptions on this endpoint id
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionInfo.request_id)
        .join(Request, ExceptionInfo.request)                  # Join Request via relationship
        .join(Endpoint, Request.endpoint)                      # Join Endpoint via Request's relationship
        .filter(Endpoint.id == endpoint_id)
        .group_by(ExceptionInfo.full_stack_trace_id)
        .count()
    )

def get_exceptions_with_timestamps(session, offset, per_page):
    """
    Gets the information about exceptions grouped by endpoint and full stack trace and sorted by latest request time.
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
            func.max(Request.time_requested).label('latest_timestamp'),
            func.min(Request.time_requested).label('first_timestamp'),
            func.count(ExceptionInfo.request_id).label('count')
        )
        .join(Request, ExceptionInfo.request)                  # Join Request via relationship
        .join(Endpoint, Request.endpoint)                      # Join Endpoint via Request's relationship
        .join(ExceptionType, ExceptionInfo.exception_type)     # Join ExceptionType via relationship
        .join(ExceptionMessage, ExceptionInfo.exception_msg)   # Join ExceptionMessage via relationship
        .group_by(Endpoint.name, ExceptionInfo.full_stack_trace_id)
        .order_by(desc('latest_timestamp'))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return result

def delete_exception(session, full_stack_trace_id: int) -> None:
    """
    Deletes an exception based on the stack trace id
    :param session: session for the database
    :param full_stack_trace_id: the stack trace id
    :return: None
    """
    session.query(ExceptionStackLine).filter(ExceptionStackLine.full_stack_trace_id == full_stack_trace_id).delete()
    result = (session.query(FullStackTrace).filter(FullStackTrace.id == full_stack_trace_id).all())
    for stack_trace in result:
        session.delete(stack_trace)
    delete_unreferenced_entries(session)
    session.query(ExceptionInfo).filter(ExceptionInfo.full_stack_trace_id == full_stack_trace_id).delete()
    session.commit()

def get_exceptions_with_timestamps_and_stacktrace_id(session, offset, per_page, endpoint_id):
    """
    Gets the information about exceptions on an endpoint grouped by full stack trace and sorted by latest request time.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: filter exceptions on this endpoint id
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - full_stack_trace_id (int) for the exceptions
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
    session.query(
            ExceptionType.type,
            ExceptionMessage.message,
            ExceptionInfo.full_stack_trace_id,
            func.max(Request.time_requested).label('latest_timestamp'),
            func.min(Request.time_requested).label('first_timestamp'),
            func.count(ExceptionInfo.request_id).label('count')
        )
        .join(Request, ExceptionInfo.request)                  # Join Request via relationship
        .join(Endpoint, Request.endpoint)                      # Join Endpoint via Request's relationship
        .join(ExceptionType, ExceptionInfo.exception_type)     # Join ExceptionType via relationship
        .join(ExceptionMessage, ExceptionInfo.exception_msg)   # Join ExceptionMessage via relationship
        .filter(Endpoint.id == endpoint_id)
        .group_by(ExceptionInfo.full_stack_trace_id)
        .order_by(desc('latest_timestamp'))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return result
