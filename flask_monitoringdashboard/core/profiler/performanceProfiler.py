from flask_monitoringdashboard.core.cache import update_duration_cache
from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.request import add_request


class PerformanceProfiler(BaseProfiler):
    """
    Used for updating the performance and utilization of the endpoint in the database.
    Used when monitoring-level == 1
    """

    def __init__(self, endpoint, ip, duration, group_by, status_code=200):
        super(PerformanceProfiler, self).__init__(endpoint)
        self._ip = ip
        self._duration = duration * 1000  # Conversion from sec to ms
        self._endpoint = endpoint
        self._group_by = group_by
        self._status_code = status_code

    def run(self):
        update_duration_cache(endpoint_name=self._endpoint.name, duration=self._duration)
        with session_scope() as db_session:
            add_request(
                db_session,
                duration=self._duration,
                endpoint_id=self._endpoint.id,
                ip=self._ip,
                group_by=self._group_by,
                status_code=self._status_code,
            )
