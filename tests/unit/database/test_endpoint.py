"""
This file contains all unit tests for the endpoint-table in the database. (Corresponding to the
file: 'flask_monitoringdashboard/database/endpoint.py')
"""
from datetime import datetime

import pytest

from flask_monitoringdashboard.database import Endpoint
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name, update_endpoint, update_last_requested, \
    get_last_requested, get_endpoints


def test_get_endpoint(session, endpoint):
    endpoint2 = get_endpoint_by_name(session, endpoint.name)
    assert endpoint.name == endpoint2.name
    assert endpoint.id == endpoint2.id


@pytest.mark.parametrize('endpoint__monitor_level', [1])
def test_update_endpoint(session, endpoint):
    update_endpoint(session, endpoint.name, 2)
    assert get_endpoint_by_name(session, endpoint.name).monitor_level == 2


@pytest.mark.parametrize('timestamp', [datetime(2020, 2, 2), datetime(2020, 3, 3)])
def test_update_last_accessed(session, endpoint, timestamp):
    update_last_requested(session, endpoint.name, timestamp=timestamp)
    result = get_value(get_last_requested(session), endpoint.name)
    assert result == timestamp


def test_endpoints(session, endpoint):
    endpoints = get_endpoints(session)
    assert endpoints.count() == session.query(Endpoint).count()
    assert [endpoint.id == e.id for e in endpoints]  # check that the endpoint is included.
