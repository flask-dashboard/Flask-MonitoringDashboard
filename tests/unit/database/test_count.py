"""
This file contains all pytests that count a number of results in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/count.py')
"""
import pytest

from flask_monitoringdashboard.database import Endpoint, Request
from flask_monitoringdashboard.database.count import (
    count_requests,
    count_total_requests,
    count_outliers,
    count_profiled_requests,
)


@pytest.fixture
def non_existing_endpoint_id(session):
    return session.query(Endpoint).count() + 1


@pytest.mark.usefixtures('request_1')
def test_count_requests(session, endpoint, non_existing_endpoint_id):
    assert count_requests(session, endpoint.id) == 1
    assert count_requests(session, non_existing_endpoint_id) == 0


def test_count_total_requests(session):
    assert count_total_requests(session) == session.query(Request).count()


@pytest.mark.usefixtures('outlier_1')
def test_count_outliers(session, endpoint, non_existing_endpoint_id):
    assert count_outliers(session, endpoint.id) == 1
    assert count_outliers(session, non_existing_endpoint_id) == 0


def test_count_profiled_requests(session, endpoint):
    assert count_profiled_requests(session, endpoint.id) == 0
