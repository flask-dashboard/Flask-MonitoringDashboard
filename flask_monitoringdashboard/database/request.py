"""
Contains all functions that access a Request object.
"""
import time
import datetime
from flask_monitoringdashboard.database import DatabaseConnectionWrapper


def get_latencies_sample(session, endpoint_id, criterion, sample_size=500):
    return DatabaseConnectionWrapper().database_connection.request_query(session).get_latencies_sample(
        endpoint_id,
        criterion,
        sample_size)


def get_error_requests_db(session, endpoint_id, *criterion):
    """
    Gets all requests that did not return a 200 status code.

    :param session: session for the database
    :param endpoint_id: ID of the endpoint to be queried
    :param criterion: Optional criteria used to file the requests.
    :return:
    """
    return DatabaseConnectionWrapper().database_connection.request_query(session).get_error_requests_db(endpoint_id,
                                                                                                        criterion)


def get_all_request_status_code_counts(session, endpoint_id):
    """
    Gets all the request status code counts.

    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :return: A list of tuples in the form of `(status_code, count)`
    """
    return DatabaseConnectionWrapper().database_connection.request_query(session).get_all_request_status_code_counts(
        endpoint_id)


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
    return DatabaseConnectionWrapper().database_connection.request_query(session).get_status_code_frequencies(
        endpoint_id,
        *criterion)


def add_request(session, duration, endpoint_id, ip, group_by, status_code):
    """ Adds a request to the database. Returns the id.
    :param status_code:  status code of the request
    :param session: session for the database
    :param duration: duration of the request
    :param endpoint_id: id of the endpoint
    :param ip: IP address of the requester
    :param group_by: a criteria by which the requests can be grouped
    :return the id of the request after it was stored in the database
    """
    database_connection_wrapper = DatabaseConnectionWrapper()
    request = database_connection_wrapper.database_connection.request(
        endpoint_id=endpoint_id,
        duration=duration,
        ip=ip,
        group_by=group_by,
        status_code=status_code,
    )
    request_query = database_connection_wrapper.database_connection.request_query(session)
    request_query.create_obj(request)
    request_query.commit()
    return request.id


def get_date_of_first_request(session):
    """ Returns the date (as unix timestamp) of the first request since FMD was deployed.
    :param session: session for the database
    :return time of the first request
    """
    current_date = DatabaseConnectionWrapper().database_connection.request_query(session).get_date_of_first_request()
    if current_date:
        try:
            return int(time.mktime(current_date.timetuple()))
        except:
            return int((current_date-datetime.datetime(1970, 1, 1)).total_seconds())
    return -1


def create_version_criterion(version):
    return DatabaseConnectionWrapper().database_connection.request_query.get_version_requested_query(version)


def create_time_based_sample_criterion(start_date, end_date):
    return DatabaseConnectionWrapper().database_connection.request_query.generate_time_query(start_date, end_date)


def get_date_of_first_request_version(session, version):
    """ Returns the date (as unix timestamp) of the first request in the current FMD version.
    :param session: session for the database
    :param version: version of the dashboard
    :return time of the first request in that version
    """
    current_date = DatabaseConnectionWrapper().database_connection.request_query(
        session).get_date_of_first_request_version(version)
    if current_date:
        try:
            return int(time.mktime(current_date.timetuple()))
        except:
            return int((current_date-datetime.datetime(1970, 1, 1)).total_seconds())
    return -1
