import threading

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed


class BaseProfiler(threading.Thread):
    """
    Only updates the last_accessed time in the database for a certain endpoint.
    Used for monitoring-level == 0
    """

    def __init__(self, endpoint):
        self._endpoint = endpoint
        threading.Thread.__init__(self)

    def run(self):
        with session_scope() as db_session:
            update_last_accessed(db_session, endpoint_name=self._endpoint.name)
