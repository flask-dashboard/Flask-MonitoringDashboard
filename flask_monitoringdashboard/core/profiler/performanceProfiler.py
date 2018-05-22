from flask_monitoringdashboard.core.profiler.baseProfiler import BaseProfiler
from flask_monitoringdashboard.database.request import add_request


class PerformanceProfiler(BaseProfiler):

    def __init__(self, thread_to_monitor, endpoint, ip):
        super(PerformanceProfiler, self).__init__(thread_to_monitor, endpoint)
        self._ip = ip

    def _on_thread_stopped(self, db_session):
        super(PerformanceProfiler, self)._on_thread_stopped(db_session)
        add_request(db_session, execution_time=self._duration, endpoint=self._endpoint, ip=self._ip)
