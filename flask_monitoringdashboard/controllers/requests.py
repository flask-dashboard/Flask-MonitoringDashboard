import datetime

import numpy

from flask_monitoringdashboard.core.timezone import to_utc_datetime, to_local_datetime
from flask_monitoringdashboard.database.count_group import count_requests_per_day, get_value
from flask_monitoringdashboard.database.endpoint import get_endpoints, get_num_requests


def get_num_requests_data(db_session, start_date, end_date):
    """
    :param db_session: session for the database
    :param start_date: datetime object
    :param end_date: datetime object and: end_date >= start_date
    :return: a list of the number of requests for each endpoint and on which day
    """
    numdays = (end_date - start_date).days + 1
    days = [start_date + datetime.timedelta(days=i) for i in range(numdays)]

    hits = count_requests_per_day(db_session, days)
    endpoints = get_endpoints(db_session)
    data = [{
        'name': end.name,
        'values': [get_value(hits_day, end.id) for hits_day in hits]
    } for end in endpoints]

    return {
        'days': [d.strftime('%Y-%m-%d') for d in days],
        'data': data
    }


def get_hourly_load(db_session, endpoint_id, start_date, end_date):
    """
    :param db_session: session for the database
    :param endpoint_id: id for the endpoint
    :param start_date: datetime object
    :param end_date: datetime object and: end_date >= start_date
    :return:
    """
    numdays = (end_date - start_date).days + 1

    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]
    heatmap_data = numpy.zeros((len(hours), numdays))

    start_datetime = to_utc_datetime(datetime.datetime.combine(start_date, datetime.time(0, 0, 0, 0)))
    end_datetime = to_utc_datetime(datetime.datetime.combine(end_date, datetime.time(23, 59, 59)))

    for time, count in get_num_requests(db_session, endpoint_id, start_datetime, end_datetime):
        parsed_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        day_index = (parsed_time - start_datetime).days
        hour_index = int(to_local_datetime(parsed_time).strftime('%H'))
        heatmap_data[hour_index][day_index] = count
    return {
        'days': [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(numdays)],
        "data": heatmap_data.tolist()
    }