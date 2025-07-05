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
