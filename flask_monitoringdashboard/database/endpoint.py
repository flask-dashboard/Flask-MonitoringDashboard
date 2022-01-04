"""
Contains all functions that access an Endpoint object
"""
import datetime
from collections import defaultdict
from flask_monitoringdashboard.database import Request, Endpoint, EndpointQuery


def get_num_requests(session, endpoint_id, start_date, end_date):
    """
    Returns a list with all dates on which an endpoint is accessed.
    :param session: session for the database
    :param endpoint_id: if None, the result is the sum of all endpoints
    :param start_date: datetime.date object
    :param end_date: datetime.date object
    :return list of dates
    """
    return group_request_times(EndpointQuery(session).get_num_requests(endpoint_id, start_date, end_date))


def group_request_times(datetimes):
    """
    Returns a list of tuples containing the number of hits per hour
    :param datetimes: list of datetime objects
    :return list of tuples ('%Y-%m-%d %H:00:00', count)
    """
    hours_dict = defaultdict(int)
    for dt in datetimes:
        round_time = dt.strftime('%Y-%m-%d %H:00:00')
        hours_dict[round_time] += 1
    return hours_dict.items()


def get_users(session, endpoint_id, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to
    filter the most used distinct.
    :param session: session for the database
    :param endpoint_id: the id of the endpoint to filter on
    :param limit: the max number of results
    :return a list of tuples (group_by, hits)
    """
    return EndpointQuery(session).get_statistics(endpoint_id,
                                                 EndpointQuery.get_field_name("group_by", Request),
                                                 limit)


def get_ips(session, endpoint_id, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to
    filter the most used distinct.
    :param session: session for the database
    :param endpoint_id: the endpoint_id to filter on
    :param limit: the number of
    :return a list with the group_by as strings.
    """
    return EndpointQuery(session).get_statistics(endpoint_id,
                                                 EndpointQuery.get_field_name("ip", Request),
                                                 limit)


def get_endpoint_by_name(session, endpoint_name):
    """
    Returns the Endpoint object from a given endpoint_name.
    If the result doesn't exist in the database, a new row is added.
    :param session: session for the database
    :param endpoint_name: string with the endpoint name
    :return Endpoint object
    """
    return EndpointQuery(session).get_endpoint_or_create(endpoint_name)


def get_endpoint_by_id(session, endpoint_id):
    """
    Returns the Endpoint object from a given endpoint id.
    :param session: session for the database
    :param endpoint_id: id of the endpoint.
    :return Endpoint object
    """
    endpoint_query = EndpointQuery(session)
    result = endpoint_query.find_by_id(Endpoint, endpoint_id)
    endpoint_query.expunge(result)
    return result


def update_endpoint(session, endpoint_name, value):
    """
    Updates the value of a specific Endpoint.
    :param session: session for the database
    :param endpoint_name: name of the endpoint
    :param value: new monitor level
    """
    EndpointQuery(session).update_endpoint(endpoint_name,
                                           EndpointQuery.get_field_name("monitor_level", Endpoint),
                                           value)


def get_last_requested(session):
    """
    Returns the accessed time of all endpoints.
    :param session: session for the database
    :return list of tuples with name of the endpoint and date it was last used
    """
    return EndpointQuery(session).get_last_requested()


def update_last_requested(session, endpoint_name, timestamp=None):
    """
    Updates the timestamp of last access of the endpoint.
    :param session: session for the database
    :param endpoint_name: name of the endpoint
    :param timestamp: optional timestamp. If not given, timestamp is current time
    """
    ts = timestamp if timestamp else datetime.datetime.utcnow()
    EndpointQuery(session).update_endpoint(endpoint_name,
                                           EndpointQuery.get_field_name("last_requested", Endpoint),
                                           ts)


def get_endpoints(session):
    """
    Returns all Endpoint objects from the database.
    :param session: session for the database
    :return list of Endpoint objects, sorted on the number of requests (descending)
    """
    return EndpointQuery(session).get_endpoints()


def get_endpoints_hits(session):
    """
    Returns all endpoint names and total hits from the database.
    :param session: session for the database
    :return list of (endpoint name, total hits) tuples
    """
    return EndpointQuery(session).get_endpoints_hits()


def get_avg_duration(session, endpoint_id):
    """ Returns the average duration of all the requests of an endpoint. If there are no requests
        for that endpoint, it returns 0.
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return average duration
    """
    return EndpointQuery(session).get_avg_duration(endpoint_id)


def get_endpoint_averages(session):
    """ Returns the average duration of all endpoints. If there are no requests for an endpoint,
        the average will be none.
    :param session: session for the database
    :return tuple of (endpoint_name, avg_duration)
    """
    return EndpointQuery(session).get_endpoint_averages()


def generate_request_error_hits_criterion():
    return EndpointQuery.generate_request_error_hits_criterion()


def filter_by_endpoint_id(endpoint_id):
    return EndpointQuery.filter_by_endpoint_id(endpoint_id)


def filter_by_time(current_time, hits_criterion=None):
    return EndpointQuery.filter_by_time(current_time, hits_criterion=hits_criterion)
