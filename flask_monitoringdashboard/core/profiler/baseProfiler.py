import threading

from flask_monitoringdashboard.core.cache import update_last_requested_cache


class BaseProfiler(threading.Thread):
    """
    Only updates the last_accessed time in the database for a certain endpoint.
    Used for monitoring-level == 0
    """

    def __init__(self, endpoint):
        self._endpoint = endpoint
        threading.Thread.__init__(self)

    def run(self):
        update_last_requested_cache(endpoint_name=self._endpoint.name)
