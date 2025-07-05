import datetime

from numpy import median
from sqlalchemy import and_

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core import cache
from flask_monitoringdashboard.core.blueprints import get_blueprint
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.measurement import add_decorator
from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime
from flask_monitoringdashboard.core.utils import simplify
from flask_monitoringdashboard.database import Request
from flask_monitoringdashboard.database.count_group import count_requests_group, get_value
from flask_monitoringdashboard.database.data_grouped import (
    get_endpoint_data_grouped,
    get_user_data_grouped,
    get_version_data_grouped,
)
from flask_monitoringdashboard.database.endpoint import (
    get_last_requested,
    get_endpoints,
    get_endpoint_by_name,
    update_endpoint,
)
from flask_monitoringdashboard.database.versions import get_first_requests
from flask_monitoringdashboard.database.exception_occurrence import count_endpoint_grouped_exceptions


def get_endpoint_overview(session):
    """
    :param session: session for the database
    :return: A list of properties for each endpoint that is found in the database
    """
    week_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    now_local = to_local_datetime(datetime.datetime.now(datetime.timezone.utc))
    today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = to_utc_datetime(today_local)

    # First flush last requested info to db
    cache.flush_cache()
    error_hits_criterion = and_(Request.status_code >= 400, Request.status_code < 600)

    hits_today = count_requests_group(session, Request.time_requested > today_utc)
    hits_today_errors = count_requests_group(
        session, and_(Request.time_requested > today_utc, error_hits_criterion)
    )

    hits_week = count_requests_group(session, Request.time_requested > week_ago)
    hits_week_errors = count_requests_group(
        session, and_(Request.time_requested > week_ago, error_hits_criterion)
    )

    hits = count_requests_group(session)

    median_today = get_endpoint_data_grouped(session, median, Request.time_requested > today_utc)
    median_week = get_endpoint_data_grouped(session, median, Request.time_requested > week_ago)
    median_overall = get_endpoint_data_grouped(session, median)
    access_times = get_last_requested(session)

    return [
        {
            'id': endpoint.id,
            'name': endpoint.name,
            'blueprint': get_blueprint(endpoint.name),
            'monitor': endpoint.monitor_level,
            'color': get_color(endpoint.name),
            'hits-today': get_value(hits_today, endpoint.id),
            'hits-today-errors': get_value(hits_today_errors, endpoint.id),
            'hits-week': get_value(hits_week, endpoint.id),
            'hits-week-errors': get_value(hits_week_errors, endpoint.id),
            'hits-overall': get_value(hits, endpoint.id),
            'median-today': get_value(median_today, endpoint.id),
            'median-week': get_value(median_week, endpoint.id),
            'median-overall': get_value(median_overall, endpoint.id),
            'last-accessed': get_value(access_times, endpoint.name, default=None),
            'exceptions': count_endpoint_grouped_exceptions(session, endpoint.id),
        }
        for endpoint in get_endpoints(session)
    ]


def get_endpoint_users(session, endpoint_id, users):
    """
    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :param users: a list of users to be filtered on
    :return: a list of dicts with the performance of each user
    """
    times = get_user_data_grouped(
        session, lambda x: simplify(x, 100), Request.endpoint_id == endpoint_id
    )
    first_requests = get_first_requests(session, endpoint_id)
    return [
        {
            'user': u,
            'date': get_value(first_requests, u),
            'values': get_value(times, u),
            'color': get_color(u),
        }
        for u in users
    ]


def get_endpoint_versions(session, endpoint_id, versions):
    """
    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :param versions: a list of version to be filtered on
    :return: a list of dicts with the performance of each version
    """
    times = get_version_data_grouped(
        session, lambda x: simplify(x, 100), Request.endpoint_id == endpoint_id
    )
    first_requests = get_first_requests(session, endpoint_id)
    return [
        {
            'version': v,
            'date': get_value(first_requests, v),
            'values': get_value(times, v),
            'color': get_color(v),
        }
        for v in versions
    ]


def get_api_performance(session, endpoints):
    """
    :param session: session for the database
    :param endpoints: a list of endpoints, encoded by their name
    :return: for every endpoint in endpoints, a list with the performance
    """
    db_endpoints = [get_endpoint_by_name(session, end) for end in endpoints]
    data = get_endpoint_data_grouped(session, lambda x: simplify(x, 10))
    return [
        {'name': end.name, 'values': get_value(data, end.id, default=[])}
        for end in db_endpoints
    ]


def set_endpoint_rule(session, endpoint_name, monitor_level):
    """
    :param session: session for the database
    :param endpoint_name: name of the endpoint
    :param monitor_level: integer, representing the monitoring-level
    """
    update_endpoint(session, endpoint_name, value=monitor_level)

    # Remove wrapper
    original = getattr(config.app.view_functions[endpoint_name], 'original', None)
    if original:
        config.app.view_functions[endpoint_name] = original
    session.commit()

    add_decorator(get_endpoint_by_name(session, endpoint_name))
