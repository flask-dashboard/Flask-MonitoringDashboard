import datetime

import numpy
from sqlalchemy import func, and_

from flask_monitoringdashboard.core.timezone import to_utc_datetime, to_local_datetime
from flask_monitoringdashboard.database import Request
from flask_monitoringdashboard.database.count_group import count_requests_per_day, get_value
from flask_monitoringdashboard.database.endpoint import get_endpoints, get_num_requests
from flask_monitoringdashboard.database.request import create_time_based_sample_criterion


def get_num_requests_data(session, start_date, end_date):
    """
    :param session: session for the database
    :param start_date: datetime object
    :param end_date: datetime object and: end_date >= start_date
    :return: a list of the number of requests for each endpoint and on which day
    """
    numdays = (end_date - start_date).days + 1
    days = [start_date + datetime.timedelta(days=i) for i in range(numdays)]

    hits = count_requests_per_day(session, days)
    endpoints = get_endpoints(session)
    data = [
        {'name': end.name, 'values': [get_value(hits_day, end.id) for hits_day in hits]}
        for end in endpoints
    ]

    return {'days': [d.strftime('%Y-%m-%d') for d in days], 'data': data}


def get_all_request_status_code_counts(session, endpoint_id):
    """
    Gets all the request status code counts.

    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :return: A list of tuples in the form of `(status_code, count)`
    """
    return (
        session.query(Request.status_code, func.count(Request.status_code))
            .filter(Request.endpoint_id == endpoint_id, Request.status_code.isnot(None))
            .group_by(Request.status_code)
            .all()
    )


def get_status_code_distribution(session, endpoint_id):
    """
    Gets the distribution of status codes returned by the given endpoint.

    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :return: A dict where the key is the status code and the value is the fraction of requests
    that returned the status
    code. Example: a return value of `{ 200: 0.92, 404: 0.08 }` means that status code 200 was
    returned on 92% of the
    requests. 8% of the requests returned a 404 status code.
    """
    status_code_counts = get_all_request_status_code_counts(session, endpoint_id)
    total_count = sum(frequency for (_, frequency) in status_code_counts)
    return {status_code: frequency / total_count for (status_code, frequency) in status_code_counts}


def get_status_code_frequencies(session, endpoint_id, *criterion):
    """
    Gets the frequencies of each status code.


    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :param criterion: Optional criteria used to file the requests.
    :return: A dict where the key is the status code and the value is the fraction of requests that returned the status
    code. Example: a return value of `{ 200: 105, 404: 3 }` means that status code 200 was returned 105 times and
    404 was returned 3 times.
    """
    status_code_counts = session.query(Request.status_code, func.count(Request.status_code)) \
        .filter(Request.endpoint_id == endpoint_id, Request.status_code.isnot(None), *criterion) \
        .group_by(Request.status_code).all()

    return dict(status_code_counts)


def get_error_requests(session, endpoint_id, *criterion):
    """
    Gets all requests that did not return a 200 status code.

    :param session: session for the database
    :param endpoint_id: ID of the endpoint to be queried
    :param criterion: Optional criteria used to file the requests.
    :return:
    """

    criteria = and_(
        Request.endpoint_id == endpoint_id,
        Request.status_code.isnot(None),
        Request.status_code >= 400,
        Request.status_code <= 599,
    )
    return session.query(Request).filter(criteria, *criterion).all()


def get_status_code_frequencies_in_interval(session, endpoint_id, criterion):
    return get_status_code_frequencies(session, endpoint_id, *criterion)


def get_hourly_load(session, endpoint_id, start_date, end_date):
    """
    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :param start_date: datetime object
    :param end_date: datetime object and: end_date >= start_date
    :return:
    """
    numdays = (end_date - start_date).days + 1

    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]
    heatmap_data = numpy.zeros((len(hours), numdays))

    start_datetime = to_utc_datetime(
        datetime.datetime.combine(start_date, datetime.time(0, 0, 0, 0))
    )
    end_datetime = to_utc_datetime(datetime.datetime.combine(end_date, datetime.time(23, 59, 59)))

    for time, count in get_num_requests(session, endpoint_id, start_datetime, end_datetime):
        parsed_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        day_index = (parsed_time - start_datetime).days
        hour_index = int(to_local_datetime(parsed_time).strftime('%H'))
        heatmap_data[hour_index][day_index] = count
    return {
        'days': [
            (start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(numdays)
        ],
        "data": heatmap_data.tolist(),
    }
