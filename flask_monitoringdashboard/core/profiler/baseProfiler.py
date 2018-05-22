import datetime
import threading

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed


class BaseProfiler(threading.Thread):
    """
    Used as a base class for the profiling levels. Also used for Profiling-level 0
    """

    def __init__(self, thread_to_monitor, endpoint):
        threading.Thread.__init__(self)
        self._thread_to_monitor = thread_to_monitor
        self._endpoint = endpoint
        self._keeprunning = True
        self._duration = 0

    def run(self):
        while self._keeprunning:
            self._run_cycle()

        # After stop has been called
        with session_scope() as db_session:
            self._on_thread_stopped(db_session)

    def _run_cycle(self):
        pass

    def stop(self, duration):
        self._duration = duration * 1000  # conversion from seconds to ms
        self._keeprunning = False
        self.join()

    def _on_thread_stopped(self, db_session):
        update_last_accessed(db_session, endpoint=self._endpoint, value=datetime.datetime.utcnow())
