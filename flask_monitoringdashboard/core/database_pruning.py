from datetime import datetime, timedelta

from flask_monitoringdashboard.database import session_scope, Request, Outlier, CustomGraphData, StackLine
from flask_monitoringdashboard.core.custom_graph import scheduler


def prune_database_older_than_weeks(weeks_to_keep, delete_custom_graph_data):
    """Prune the database of Request and optionally CustomGraph data older than the specified number of weeks"""
    with session_scope() as session:
        date_to_delete_from = datetime.utcnow() - timedelta(weeks=weeks_to_keep)

        # Prune Request table and related Outlier entries
        requests_to_delete = session.query(Request).filter(Request.time_requested < date_to_delete_from).all()

        for request in requests_to_delete:
            session.query(Outlier).filter(Outlier.request_id == request.id).delete()
            session.query(StackLine).filter(StackLine.request_id == request.id).delete()

        session.query(Request).filter(Request.time_requested < date_to_delete_from).delete()

        if delete_custom_graph_data:
            session.query(CustomGraphData).filter(CustomGraphData.time < date_to_delete_from).delete()

        session.commit()


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
