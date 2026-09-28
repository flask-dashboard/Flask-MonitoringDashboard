"""
This file contains all unit tests of exception info in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_occurrence.py')
"""

from flask_monitoringdashboard.database import ExceptionOccurrence
from flask_monitoringdashboard.database.exception_occurrence import (
    add_exception_occurrence,
    count_grouped_exceptions,
    count_endpoint_grouped_exceptions,
    count_grouped_exceptions_per_endpoint,
    get_exceptions_with_timestamps,
    delete_exception_group,
    get_exceptions_with_timestamps_and_stack_trace_id,
)


def test_count_grouped_exceptions(session, request_1):
    """
    Test the count_grouped_exceptions function to ensure it correctly counts grouped exceptions.
    They should be grouped by stack_trace_snapshot_id
    """
    stack_trace_snapshot_id = 100
    delete_exception_group(session, stack_trace_snapshot_id)

    count_grouped_before = count_grouped_exceptions(session)
    count_occurences_before = session.query(ExceptionOccurrence).count()

    exception_occurrence_1 = ExceptionOccurrence(
        request_id=request_1.id,
        exception_type_id=2,
        exception_msg_id=3,
        stack_trace_snapshot_id=stack_trace_snapshot_id,
        is_user_captured=True,
    )
    exception_occurrence_2 = ExceptionOccurrence(
        request_id=request_1.id,
        exception_type_id=2,
        exception_msg_id=3,
        stack_trace_snapshot_id=stack_trace_snapshot_id,
        is_user_captured=True,
    )
    session.add(exception_occurrence_1)
    session.add(exception_occurrence_2)
    session.commit()

    count_grouped_after = count_grouped_exceptions(session)
    count_occurences_after = session.query(ExceptionOccurrence).count()

    assert count_grouped_before + 1 == count_grouped_after
    assert count_occurences_before + 2 == count_occurences_after


def test_count_grouped_exceptions_per_endpoint(session, request_1):
    """The one-query count must agree with count_endpoint_grouped_exceptions for every endpoint."""
    for stack_trace_snapshot_id in (201, 202, 202):
        session.add(
            ExceptionOccurrence(
                request_id=request_1.id,
                exception_type_id=2,
                exception_msg_id=3,
                stack_trace_snapshot_id=stack_trace_snapshot_id,
                is_user_captured=True,
            )
        )
    session.commit()

    per_endpoint = count_grouped_exceptions_per_endpoint(session)

    assert per_endpoint[request_1.endpoint_id] >= 2
    for endpoint_id, count in per_endpoint.items():
        assert count == count_endpoint_grouped_exceptions(session, endpoint_id)
