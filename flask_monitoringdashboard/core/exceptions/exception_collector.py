from types import TracebackType
from typing import Union

from sqlalchemy.orm import Session
from flask_monitoringdashboard.core.exceptions.scoped_exception_collector import (
    ScopedExceptionCollector,
)
from flask_monitoringdashboard.core.exceptions.stack_frame_parsing import (
    get_function_definition_from_frame,
)
from flask_monitoringdashboard.core.exceptions.stack_trace_hashing import (
    hash_stack_trace,
)
from flask_monitoringdashboard.database.exception_occurrence import (
    add_exception_occurrence,
)
from flask_monitoringdashboard.database.stack_trace_snapshot import (
    add_stack_trace_snapshot,
    get_stack_trace_by_hash,
)
from flask_monitoringdashboard.database.exception_stack_line import (
    add_exception_stack_line,
)
from flask_monitoringdashboard.database.exception_frame import add_exception_frame
from flask_monitoringdashboard.database.function_location import add_function_location
from flask_monitoringdashboard.database.file_path import add_file_path
from flask_monitoringdashboard.database.function_definition import (
    add_function_definition,
)
from flask_monitoringdashboard.database.exception_message import add_exception_message
from flask_monitoringdashboard.database.exception_type import add_exception_type


class ExceptionCollector:

    def __init__(self, scoped_logger: ScopedExceptionCollector):
        self.user_captured_exceptions: list[BaseException] = (
            scoped_logger.user_captured_exceptions
        )
        self.uncaught_exception: Union[BaseException, None] = (
            scoped_logger.uncaught_exception
        )

    def save_to_db(self, request_id: int, session: Session):
        """
        Iterates over all the user captured exceptions and also a possible uncaught one, and saves each exception to the DB
        """
        for e in self.user_captured_exceptions:
            save_exception_occurence_to_db(
                request_id, session, e, type(e), e.__traceback__, True
            )

        e = self.uncaught_exception
        if e is not None:
            if e.__traceback__ is not None:
                # We have to choose the next frame as else it will include the evaluate function from measurement.py in the traceback
                # where it was temporaritly captured for logging by the ScopedExceptionCollector, before getting reraised later
                e = e.with_traceback(e.__traceback__.tb_next)

            save_exception_occurence_to_db(
                request_id, session, e, type(e), e.__traceback__, False
            )


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
        trace_id = int(existing_trace.id)
    else:
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
    add_exception_occurrence(
        session, request_id, trace_id, exc_type_id, exc_msg_id, is_user_captured
    )
