from datetime import datetime, timedelta

from flask_monitoringdashboard.core.custom_graph import scheduler
from flask_monitoringdashboard.database import ( 
    session_scope, 
    Request, Outlier, StackLine, CustomGraphData, ExceptionInfo, FullStackTrace, ExceptionStackLine, FunctionDefinition
)

def prune_database_older_than_weeks(weeks_to_keep, delete_custom_graph_data):
    """Prune the database of Request and optionally CustomGraph data older than the specified number of weeks"""
    with session_scope() as session:
        date_to_delete_from = datetime.utcnow() - timedelta(weeks=weeks_to_keep)

        # Prune Request table and related Outlier entries
        requests_to_delete = session.query(Request).filter(Request.time_requested < date_to_delete_from).all()

        for request in requests_to_delete:
            session.query(Outlier).filter(Outlier.request_id == request.id).delete()
            session.query(StackLine).filter(StackLine.request_id == request.id).delete()
            session.query(ExceptionInfo).filter(ExceptionInfo.request_id == request.id).delete()
            session.delete(request)

        if delete_custom_graph_data:
            session.query(CustomGraphData).filter(CustomGraphData.time < date_to_delete_from).delete()
            
        delete_entries_unreferenced_by_exception_info(session)

        session.commit()

def delete_entries_unreferenced_by_exception_info(session):
    """Delete FullStackTraces, ExceptionStackLines, FunctionDefinitions that are not referenced by any ExceptionInfos"""

    # Find and delete FullStackTraces (along with their ExceptionStackLines) that are not referenced by any ExceptionInfos
    full_stack_traces_to_delete = session.query(FullStackTrace).filter(
        ~session.query(ExceptionInfo)
        .filter(ExceptionInfo.full_stack_trace_id == FullStackTrace.id)
        .exists()
    ).all()

    for full_stack_trace in full_stack_traces_to_delete:
        session.query(ExceptionStackLine).filter(ExceptionStackLine.full_stack_trace_id == full_stack_trace.id).delete()
        session.delete(full_stack_trace)
        
    # Find and delete FunctionDefenitions that are not referenced by any ExceptionStackLines
    function_definitions_to_delete = session.query(FunctionDefinition).filter(
        ~session.query(ExceptionStackLine)
        .filter(ExceptionStackLine.function_definition_id == FunctionDefinition.id)
        .exists()
    ).all()
    
    for function_definition in function_definitions_to_delete:
        session.delete(function_definition)


def add_background_pruning_job(weeks_to_keep, delete_custom_graph_data, **schedule):
    """Add a scheduled job to prune the database of Request and optionally CustomGraph data older than the specified
    number of weeks"""

    scheduler.add_job(
        id='database_pruning_schedule',
        func=prune_database_older_than_weeks,
        args=[weeks_to_keep, delete_custom_graph_data],  # These are arguments passed to the prune function
        trigger='cron',
        replace_existing=True,  # This will replace an existing job
        **schedule
    )
