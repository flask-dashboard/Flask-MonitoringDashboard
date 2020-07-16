from datetime import datetime
from random import randint

import pytest

from flask_monitoringdashboard.database import Request
from flask_monitoringdashboard.database.count_group import (
    count_requests_group,
    count_requests_per_day,
)


def test_count_requests_group(session, request_1, endpoint):
    assert count_requests_group(session, Request.version_requested == request_1.version_requested) == [(endpoint.id, 1)]


@pytest.mark.parametrize('request_1__time_requested', [datetime(1970 + randint(0, 1000), 1, 2)])
def test_count_requests_per_day(session, request_1, endpoint):
    assert count_requests_per_day(session, []) == []

    assert count_requests_per_day(session, [request_1.time_requested.date()]) == [[(endpoint.id, 1)]]
