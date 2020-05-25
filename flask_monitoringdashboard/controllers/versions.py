import numpy

from flask_monitoringdashboard.database import Request
from flask_monitoringdashboard.database.count_group import get_value, count_requests_group
from flask_monitoringdashboard.database.data_grouped import get_two_columns_grouped
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name
from flask_monitoringdashboard.database.versions import get_first_requests


def get_2d_version_data(session, endpoint_id, versions, column_data, column):
    """
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :param versions: a list of versions
    :param column_data: a is of the other column
    :param column: column from the Request table
    :return: a dict with 2d information about the version and another column
    """
    first_request = get_first_requests(session, endpoint_id)
    values = get_two_columns_grouped(session, column, Request.endpoint_id == endpoint_id)
    data = [[get_value(values, (data, v)) for v in versions] for data in column_data]

    return {
        'versions': [{'version': v, 'date': get_value(first_request, v)} for v in versions],
        'data': data,
    }


def get_version_user_data(session, endpoint_id, versions, users):
    return get_2d_version_data(session, endpoint_id, versions, users, Request.group_by)


def get_version_ip_data(session, endpoint_id, versions, ips):
    return get_2d_version_data(session, endpoint_id, versions, ips, Request.ip)


def get_multi_version_data(session, endpoints, versions):
    """
    :param session: session for the database
    :param endpoints: a list of all endpoints for which the data must be
        collected (represented by their name)
    :param versions: a list of versions
    :return: a 2d list of data
    """
    endpoints = [get_endpoint_by_name(session, name) for name in endpoints]
    requests = [count_requests_group(session, Request.version_requested == v) for v in versions]

    total_hits = numpy.zeros(len(versions))
    hits = numpy.zeros((len(endpoints), len(versions)))

    for i, _ in enumerate(versions):
        total_hits[i] = max(1, sum([value for key, value in requests[i]]))

    for j, _ in enumerate(endpoints):
        for i, _ in enumerate(versions):
            hits[j][i] = get_value(requests[i], endpoints[j].id) * 100 / total_hits[i]
    return hits.tolist()
