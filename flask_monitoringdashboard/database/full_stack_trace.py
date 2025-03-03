from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import ExceptionStackLine, FullStackTrace
from sqlalchemy import desc

def get_stack_trace_by_hash(session: Session, full_stack_trace: str) -> FullStackTrace | None:
    """
    Get FullStackTrace record by its stack_trace_hash.
    """
    result = (
        session.query(FullStackTrace)
        .filter_by(stack_trace_hash=full_stack_trace)
        .first()
    )
    return result

def add_full_stack_trace(session: Session, full_stack_trace: str) -> int:
    """
    Add a new FullStackTrace record.
    """
    result = FullStackTrace(
        stack_trace_hash = full_stack_trace
    )
    session.add(result)
    session.flush()

    return int(result.id)


def get_stacklines_from_full_stacktrace_id(session: Session, full_stack_trace_id: int) -> list[ExceptionStackLine]:
    """
    Gets all the stack lines referred to by a stacktrace.
    :param session: session for the database
    :param full_stack_trace_id: Filter ExceptionStackLines on this stack trace id
    :return: A list of ExceptionStackLine objects of a specific stack trace
    """
    result = (
        session.query(
            ExceptionStackLine
        )
        .filter(ExceptionStackLine.full_stack_trace_id == full_stack_trace_id)
        .order_by(desc(ExceptionStackLine.position))
        .all()
    )
    return result

