"""
    Contains the in memory cache used to increase the FMD performance.
"""
from multiprocessing import Lock

from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_last_requested, get_endpoints_hits, get_endpoint_averages


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

    def update_last_requested(self, last_requested):
        with mutex:
            self.last_requested = last_requested

    def update_duration(self, duration):
        with mutex:
            self.average_duration = (self.average_duration * self.hits + duration)/float(self.hits + 1)
            self.hits += 1


def display_cache():
    global memory_cache
    for k in memory_cache.keys():
        print('%s : last=%s, avg=%f, hits=%d' % (k, memory_cache[k].last_requested,
                                                 memory_cache[k].average_duration, memory_cache[k].hits))


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
        display_cache()
