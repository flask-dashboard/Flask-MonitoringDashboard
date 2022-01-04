from flask_monitoringdashboard.database import Request, VersionQuery


def get_field_name(name):
    return VersionQuery.get_field_name(name, Request)


def get_version_requested_query(v):
    return VersionQuery.get_version_requested_query(v)


def get_versions(session, endpoint_id=None, limit=None):
    """
    Returns a list of length 'limit' with the versions that are used in the application
    :param session: session for the database
    :param endpoint_id: only get the version that are used in this endpoint
    :param limit: only return the most recent versions
    :return: a list of tuples with the versions (as a string) and dates, from oldest to newest
    """
    return VersionQuery(session).get_versions(endpoint_id=endpoint_id, limit=limit)


def get_2d_version_data_filter(endpoint_id):
    return VersionQuery.get_2d_version_data_filter(endpoint_id)


def get_first_requests(session, endpoint_id, limit=None):
    """
    Returns a list with all versions and when they're first used
    :param session: session for the database
    :param limit: only return the most recent versions
    :param endpoint_id: id of the endpoint
    :return list of tuples with versions
    """
    return VersionQuery(session).get_first_requests(endpoint_id, limit=limit)
