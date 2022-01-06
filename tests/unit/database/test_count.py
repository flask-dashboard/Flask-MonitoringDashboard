"""
This file contains all pytests that count a number of results in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/count.py')
"""
import pytest

from flask_monitoringdashboard.database.count import (
    count_requests,
    count_total_requests,
    count_outliers,
    count_profiled_requests,
)
from flask_monitoringdashboard.database import DatabaseConnectionWrapper


database_connection_wrapper = DatabaseConnectionWrapper()


Request = database_connection_wrapper.database_connection.request
RequestQuery = database_connection_wrapper.database_connection.request_query
Endpoint = database_connection_wrapper.database_connection.endpoint
EndpointQuery = database_connection_wrapper.database_connection.endpoint_query


@pytest.fixture
def non_existing_endpoint_id(session):
    return EndpointQuery(session).count(Endpoint) + 1


@pytest.mark.usefixtures('request_1')
def test_count_requests(session, endpoint, non_existing_endpoint_id):
    assert count_requests(session, endpoint.id) == 1
    assert count_requests(session, non_existing_endpoint_id) == 0


def test_count_total_requests(session):
    assert count_total_requests(session) == RequestQuery(session).count(Request)


@pytest.mark.usefixtures('outlier_1')
def test_count_outliers(session, endpoint, non_existing_endpoint_id):
    assert count_outliers(session, endpoint.id) == 1
    assert count_outliers(session, non_existing_endpoint_id) == 0


def test_count_profiled_requests(session, endpoint):
    assert count_profiled_requests(session, endpoint.id) == 0
