"""
    Contains the in memory cache used to increase the FMD performance.
"""
import datetime
from multiprocessing import Lock

from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_last_requested, get_endpoints_hits, get_endpoint_averages, \
    update_last_requested

memory_cache = {}
mutex = Lock()


class EndpointInfo(object):
    """
    Info about an endpoint that is stored in the memory cache.
    """
    def __init__(self, last_requested=None, average_duration=None, hits=None):
        self.last_requested = last_requested
        self.average_duration = average_duration if average_duration else 0
        self.hits = hits if hits else 0

    def set_last_requested(self, last_requested):
        with mutex:
            self.last_requested = last_requested

    def set_duration(self, duration):
        with mutex:
            self.average_duration = (self.average_duration * self.hits + duration)/float(self.hits + 1)
            self.hits += 1

    def get_duration(self):
        with mutex:
            return self.average_duration


def display_cache():
    """
    Debug purposes.
    """
    global memory_cache
    print('++++++++++++++++++++++display cache')
    for k in memory_cache.keys():
        print('%s : last=%s, avg=%f, hits=%d' % (k, memory_cache[k].last_requested,
                                                 memory_cache[k].average_duration, memory_cache[k].hits))
    print('++++++++++++++++++++++display cache ended')


def init_cache():
    """
    This should be added to the list of functions that are executed before the first request.
    It initializes the in memory cache from the db
    """
    global memory_cache
    with session_scope() as db_session:
        last_req_dict = dict(get_last_requested(db_session))
        hits_dict = dict(get_endpoints_hits(db_session))
        averages_dict = dict(get_endpoint_averages(db_session))
        for rule in get_rules():
            memory_cache[rule.endpoint] = EndpointInfo(last_requested=last_req_dict.get(rule.endpoint),
                                                       average_duration=averages_dict.get(rule.endpoint),
                                                       hits=hits_dict.get(rule.endpoint))


def update_last_requested_cache(endpoint_name):
    """
    Use this instead of updating the last requested to the database.
    """
    global memory_cache
    memory_cache.get(endpoint_name).set_last_requested(datetime.datetime.utcnow())


def update_duration_cache(endpoint_name, duration):
    """
    Use this together with adding a request to the database.
    """
    global memory_cache
    memory_cache.get(endpoint_name).set_last_requested(datetime.datetime.utcnow())
    memory_cache.get(endpoint_name).set_duration(duration)


def get_avg_endpoint(endpoint_name):
    """
    Return the average of the request duration for an endpoint.
    """
    global memory_cache
    return memory_cache.get(endpoint_name).get_duration()


def get_last_requested_overview():
    """
    Get the last requested values from the cache for the overview page.
    """
    global memory_cache
    access_times = []
    for endpoint_name, endpoint_info in memory_cache.items():
        access_times.append((endpoint_name, endpoint_info.last_requested))
    return access_times


def flush_cache():
    """
    Flushes cache changes to the db. To be called at shut down.
    """
    global memory_cache
    with session_scope() as db_session:
        for endpoint_name, endpoint_info in memory_cache.items():
            update_last_requested(db_session, endpoint_name, endpoint_info.last_requested)
