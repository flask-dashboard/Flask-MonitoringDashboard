from datetime import datetime, timedelta

from flask_monitoringdashboard.database import session_scope, Request, Outlier, StackLine, CustomGraphData, CustomGraph

from sqlalchemy import func
from datetime import datetime, timedelta


def prune_database_older_than_weeks(weeks, delete_custom_graphs):
    """Prune the database of Request and optionally CustomGraph data older than the specified number of weeks"""
    with session_scope() as session:
        date_to_delete_from = datetime.utcnow() - timedelta(weeks=weeks)

        # Prune Request table and related Outlier and StackLine entries
        old_requests = session.query(Request).filter(Request.time_requested < date_to_delete_from).all()
        for request in old_requests:
            session.delete(request)

        # Prune CustomGraphData table by joining with CustomGraph to get the time_added
        if delete_custom_graphs:
            old_graph_data = session.query(CustomGraphData) \
                .join(CustomGraph, CustomGraph.graph_id == CustomGraphData.graph_id) \
                .filter(CustomGraph.time_added < date_to_delete_from).all()
            for graph_data in old_graph_data:
                session.delete(graph_data)

        session.commit()



