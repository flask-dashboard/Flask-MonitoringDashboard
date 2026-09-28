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


PRUNE_BATCH_SIZE = 10000


def prune_database_older_than_weeks(weeks_to_keep, delete_custom_graph_data,
                                    batch_size=PRUNE_BATCH_SIZE):
    """Prune the database of Request and optionally CustomGraph data older than the specified
    number of weeks.

    Requests are deleted in batches, each in its own transaction, together with the rows that
    reference them. Memory and lock time stay bounded however large the backlog is, and since a
    batch only deletes rows that still exist, two processes pruning at the same time is wasteful
    but harmless."""
    date_to_delete_from = datetime.now(timezone.utc) - timedelta(weeks=weeks_to_keep)

    while _prune_request_batch(date_to_delete_from, batch_size) == batch_size:
        pass

    with session_scope() as session:
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


def _prune_request_batch(date_to_delete_from, batch_size):
    """Delete up to batch_size Requests older than date_to_delete_from, and the Outliers,
    StackLines and ExceptionOccurrences that reference them. Returns how many Requests went."""
    with session_scope() as session:
        request_ids = [
            request_id
            for (request_id,) in session.query(Request.id)
            .filter(Request.time_requested < date_to_delete_from)
            .limit(batch_size)
        ]
        if not request_ids:
            return 0

        for model in (Outlier, StackLine, ExceptionOccurrence):
            session.query(model).filter(model.request_id.in_(request_ids)).delete(
                synchronize_session=False
            )
        session.query(Request).filter(Request.id.in_(request_ids)).delete(
            synchronize_session=False
        )
        return len(request_ids)


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
