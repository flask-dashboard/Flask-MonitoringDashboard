import pkg_resources
from flask import url_for
from werkzeug.routing import BuildError
import numpy as np

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database.endpoint import get_monitor_rule
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.function_calls import get_date_of_first_request


def get_endpoint_details(endpoint):
    """ Return details about an endpoint"""
    return {
        'endpoint': endpoint,
        'rule': get_monitor_rule(endpoint),
        'url': get_url(endpoint),
        'total_hits': count_requests(endpoint)
    }


def get_details():
    """ Return details about the deployment """
    return {
        'link': config.link,
        'dashboard-version': pkg_resources.require("Flask-MonitoringDashboard")[0].version,
        'config-version': config.version,
        'first-request': get_date_of_first_request()
    }


def formatter(ms):
    """
    formats the ms into seconds and ms
    :param ms: the number of ms
    :return: a string representing the same amount, but now represented in seconds and ms.
    """
    sec = int(ms) // 1000
    ms = int(ms) % 1000
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}.{1}s'.format(sec, ms)


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
    return [np.percentile(values, i * 100 // (n-1)) for i in range(n)]
