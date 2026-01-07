from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from flask_monitoringdashboard.core.custom_graph import scheduler
from flask_monitoringdashboard.database import (
    CodeLine,
    ExceptionMessage,
    ExceptionType,
    session_scope,
    Request,
    Outlier,
    StackLine,
    CustomGraphData,
    ExceptionOccurrence,
    StackTraceSnapshot,
    ExceptionStackLine,
    ExceptionFrame,
    FunctionLocation,
    FilePath,
    FunctionDefinition,
)


def prune_database_older_than_weeks(weeks_to_keep, delete_custom_graph_data):
    """Prune the database of Request and optionally CustomGraph data older than the specified number of weeks"""
    with session_scope() as session:
        date_to_delete_from = datetime.now(timezone.utc) - timedelta(weeks=weeks_to_keep)

        # Prune Request table and related Outlier entries
        requests_to_delete = (
            session.query(Request)
            .filter(Request.time_requested < date_to_delete_from)
            .all()
        )

        for request in requests_to_delete:
            session.query(Outlier).filter(Outlier.request_id == request.id).delete()
            session.query(StackLine).filter(StackLine.request_id == request.id).delete()
            session.query(ExceptionOccurrence).filter(
                ExceptionOccurrence.request_id == request.id
            ).delete()
            session.delete(request)

        # Find and delete CodeLines not referenced by any StackLines
        session.query(CodeLine).filter(
            ~session.query(StackLine).filter(StackLine.code_id == CodeLine.id).exists()
        ).delete(synchronize_session=False)

        if delete_custom_graph_data:
            session.query(CustomGraphData).filter(
                CustomGraphData.time < date_to_delete_from
            ).delete()

        delete_entries_unreferenced_by_exception_occurrence(session)

        session.commit()


def prune_database_older_than_days(days_to_keep):
    """Prune the database of Request data older than the specified number of days.

    Uses batch deletes with subqueries for better performance on large tables.
    Does NOT delete CustomGraphData - only request-related tables are cleaned up.

    :param days_to_keep: Number of days of data to retain
    """
    with session_scope() as session:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        # Get subquery for old request IDs - used for batch deletes
        old_request_ids = session.query(Request.id).filter(
            Request.time_requested < cutoff_date
        ).subquery().select()

        # Batch delete child tables first (respecting FK relationships)
        session.query(Outlier).filter(
            Outlier.request_id.in_(old_request_ids)
        ).delete(synchronize_session=False)

        session.query(StackLine).filter(
            StackLine.request_id.in_(old_request_ids)
        ).delete(synchronize_session=False)

        session.query(ExceptionOccurrence).filter(
            ExceptionOccurrence.request_id.in_(old_request_ids)
        ).delete(synchronize_session=False)

        # Delete parent Request records
        session.query(Request).filter(
            Request.time_requested < cutoff_date
        ).delete(synchronize_session=False)

        # Find and delete CodeLines not referenced by any StackLines
        session.query(CodeLine).filter(
            ~session.query(StackLine).filter(StackLine.code_id == CodeLine.id).exists()
        ).delete(synchronize_session=False)

        # Clean up orphaned exception-related records
        delete_entries_unreferenced_by_exception_occurrence(session)

        session.commit()


def delete_entries_unreferenced_by_exception_occurrence(session: Session):
    """
    Delete ExceptionTypes, ExceptionMessages, StackTraceSnapshots (along with their ExceptionStackLines) 
    that are not referenced by any ExceptionOccurrences, 
    ExceptionFrames that are not referenced by any ExceptionStackLines,
    FunctionLocations that are not referenced by any ExceptionFrames, 
    FilePaths and FunctionDefinitions that are not referenced by any FunctionLocations, and
    CodeLines that are not referenced by any ExceptionStackLines and not referenced by any StackLines
    """
    # Delete ExceptionTypes that are not referenced by any ExceptionOccurrences
    session.query(ExceptionType).filter(
        ~session.query(ExceptionOccurrence)
        .filter(ExceptionOccurrence.exception_type_id == ExceptionType.id)
        .exists()
    ).delete(synchronize_session=False)

    # Delete ExceptionMessages that are not referenced by any ExceptionOccurrences
    session.query(ExceptionMessage).filter(
        ~session.query(ExceptionOccurrence)
        .filter(ExceptionOccurrence.exception_msg_id == ExceptionMessage.id)
        .exists()
    ).delete(synchronize_session=False)

    # Find and delete StackTraceSnapshots (along with their ExceptionStackLines) that are not referenced by any ExceptionOccurrences
    stack_trace_snapshots_to_delete = (
        session.query(StackTraceSnapshot)
        .filter(
            ~session.query(ExceptionOccurrence)
            .filter(ExceptionOccurrence.stack_trace_snapshot_id == StackTraceSnapshot.id)
            .exists()
        )
        .all()
    )
    for stack_trace_snapshot in stack_trace_snapshots_to_delete:
        session.query(ExceptionStackLine).filter(
            ExceptionStackLine.stack_trace_snapshot_id == stack_trace_snapshot.id
        ).delete()
        session.delete(stack_trace_snapshot)

    # Delete ExceptionFrames that are not referenced by any ExceptionStackLines
    session.query(ExceptionFrame).filter(
        ~session.query(ExceptionStackLine)
        .filter(ExceptionStackLine.exception_frame_id == ExceptionFrame.id)
        .exists()
    ).delete(synchronize_session=False)

    # Delete FunctionLocations that are not referenced by any ExceptionFrames
    session.query(FunctionLocation).filter(
        ~session.query(ExceptionFrame)
        .filter(ExceptionFrame.function_location_id == FunctionLocation.id)
        .exists()
    ).delete(synchronize_session=False)

    # Delete FilePaths that are not referenced by any FunctionLocations
    session.query(FilePath).filter(
        ~session.query(FunctionLocation)
        .filter(FunctionLocation.file_path_id == FilePath.id)
        .exists()
    ).delete(synchronize_session=False)

    # Delete FunctionDefinitions that are not referenced by any FunctionLocations
    session.query(FunctionDefinition).filter(
        ~session.query(FunctionLocation)
        .filter(FunctionLocation.function_definition_id == FunctionDefinition.id)
        .exists()
    ).delete(synchronize_session=False)


def add_background_pruning_job(weeks_to_keep, delete_custom_graph_data, **schedule):
    """Add a scheduled job to prune the database of Request and optionally CustomGraph data older than the specified
    number of weeks"""

    scheduler.add_job(
        id="database_pruning_schedule",
        func=prune_database_older_than_weeks,
        args=[
            weeks_to_keep,
            delete_custom_graph_data,
        ],  # These are arguments passed to the prune function
        trigger="cron",
        replace_existing=True,  # This will replace an existing job
        **schedule
    )


def schedule_automatic_pruning(days_to_keep):
    """Schedule automatic data retention cleanup to run daily at 2 AM.

    This function is called automatically by dashboard.bind() when
    config.data_retention_days is greater than 0.

    :param days_to_keep: Number of days of data to retain
    """
    scheduler.add_job(
        id="automatic_data_retention",
        func=prune_database_older_than_days,
        args=[days_to_keep],
        trigger="cron",
        hour=2,
        minute=0,
        replace_existing=True,
    )
