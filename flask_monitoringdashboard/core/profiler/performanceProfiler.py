from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.database.request import add_request, get_avg_execution_time
from flask_monitoringdashboard import config


class PerformanceProfiler(BaseProfiler):

    def __init__(self, thread_to_monitor, endpoint, ip):
        super(PerformanceProfiler, self).__init__(thread_to_monitor, endpoint)
        self._ip = ip
        self._request_id = None
        self._avg_endpoint = None
        self._is_outlier = None

    def _on_thread_stopped(self, db_session):
        super(PerformanceProfiler, self)._on_thread_stopped(db_session)
        self._avg_endpoint = get_avg_execution_time(db_session, self._endpoint)
        if not self._avg_endpoint:
            self._is_outlier = False
            self._request_id = add_request(db_session, execution_time=self._duration, endpoint=self._endpoint,
                                           ip=self._ip, is_outlier=self._is_outlier)
            return

        self._is_outlier = self._duration > config.outlier_detection_constant * self._avg_endpoint
        self._request_id = add_request(db_session, execution_time=self._duration, endpoint=self._endpoint,
                                       ip=self._ip, is_outlier=self._is_outlier)
