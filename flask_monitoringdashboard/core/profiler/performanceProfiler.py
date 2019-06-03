from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import update_last_requested
from flask_monitoringdashboard.database.request import add_request
from flask_monitoringdashboard.core.cache import update_last_requested_cache


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
        update_last_requested_cache(endpoint_name=self._endpoint.name)
        with session_scope() as db_session:
            add_request(db_session, duration=self._duration, endpoint_id=self._endpoint.id, ip=self._ip)
