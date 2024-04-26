import numpy as np
from flask import url_for
from werkzeug.routing import BuildError

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database.count import count_requests, count_total_requests
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_id
from flask_monitoringdashboard.database.request import (
    get_date_of_first_request,
    get_date_of_first_request_version,
)
from flask_monitoringdashboard import telemetry_config


def get_endpoint_details(session, endpoint_id):
    """
    Returns details about an endpoint.
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return dictionary
    """
    endpoint = get_endpoint_by_id(session, endpoint_id)
    endpoint.time_added = to_local_datetime(endpoint.time_added)
    flask_rule = get_rules(endpoint.name)
    methods = [list(rule.methods) for rule in flask_rule]
    methods = sum(methods, [])  # flatten list
    return {
        'id': endpoint_id,
        'color': get_color(endpoint.name),
        'methods': list(dict.fromkeys(methods)),
        'endpoint': endpoint.name,
        'rules': [r.rule for r in get_rules(endpoint.name)],
        'monitor-level': endpoint.monitor_level,
        'url': get_url(endpoint.name),
        'total_hits': count_requests(session, endpoint.id),
    }


def get_details(session):
    """
    Returns details about the deployment.
    :param session: session for the database
    :return dictionary
    """
    import json
    from flask_monitoringdashboard import loc

    with open(loc() + 'constants.json', 'r') as f:
        constants = json.load(f)

    return {
        'link': config.link,
        'dashboard-version': constants['version'],
        'config-version': config.version,
        'first-request': get_date_of_first_request(session),
        'first-request-version': get_date_of_first_request_version(session, config.version),
        'total-requests': count_total_requests(session),
        'fmd-id': telemetry_config.fmd_user,
    }


def get_url(end):
    """
    Returns the URL if possible.
    URL's that require additional arguments, like /static/<file> cannot be retrieved.
    :param end: the endpoint for the url.
    :return: the url_for(end) or None,
    """
    try:
        return url_for(end)
    except BuildError:
        return None


def simplify(values, n=5):
    """
    Simplify a list of values. It returns a list that is representative for the input
    :param values: list of values
    :param n: length of the returned list
    :return: list with n values: min, q1, median, q3, max
    """
    if len(values) <= n:
        return values
    return [np.percentile(values, i * 100 // (n - 1)) for i in range(n)]
