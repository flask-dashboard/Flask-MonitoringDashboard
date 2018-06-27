from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_accessed
from flask_monitoringdashboard.database.request import add_request


class PerformanceProfiler(BaseProfiler):
    """
    Used for updating the performance and utilization of the endpoint in the database.
    Used when monitoring-level == 1
    """

    def __init__(self, endpoint, ip, duration):
        super(PerformanceProfiler, self).__init__(endpoint)
        self._ip = ip
        self._duration = duration * 1000  # Conversion from sec to ms
        self._endpoint = endpoint

    def run(self):
        with session_scope() as db_session:
            update_last_accessed(db_session, endpoint_name=self._endpoint.name)
            add_request(db_session, duration=self._duration, endpoint_id=self._endpoint.id, ip=self._ip)
