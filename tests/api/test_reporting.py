import sys
from datetime import datetime, timedelta
import pytest

from flask_monitoringdashboard.database import Endpoint


def test_make_report_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/reporting/make_report/intervals')
    assert not response.is_json


@pytest.mark.parametrize('request_1__time_requested', [datetime.utcnow() - timedelta(hours=6)])
@pytest.mark.parametrize('request_1__duration', [5000])
@pytest.mark.parametrize('request_1__status_code', [500])
@pytest.mark.parametrize('request_2__time_requested', [datetime.utcnow() - timedelta(days=1, hours=6)])
@pytest.mark.parametrize('request_2__duration', [100])
@pytest.mark.skipif(sys.version_info < (3, ), reason="For some reason, this doesn't work in python 2.7.")
def test_make_report_post_not_significant(dashboard_user, endpoint, request_1, request_2, session):
    epoch = datetime(1970, 1, 1)
    response = dashboard_user.post(
        'dashboard/api/reporting/make_report/intervals',
        json={
            'interval': {
                'from': (datetime.utcnow() - timedelta(days=1) - epoch).total_seconds(),
                'to': (datetime.utcnow() - epoch).total_seconds(),
            },
            'baseline_interval': {
                'from': (datetime.utcnow() - timedelta(days=2) - epoch).total_seconds(),
                'to': (datetime.utcnow() - timedelta(days=1) - epoch).total_seconds(),
            },
        },
    )
    assert response.status_code == 200

    assert len(response.json['summaries']) == session.query(Endpoint).count()
    [data] = [row for row in response.json['summaries'] if row['endpoint_id'] == endpoint.id]

    assert data['endpoint_id'] == endpoint.id
    assert data['endpoint_name'] == endpoint.name
    assert not data['has_anything_significant']

    question1, question2 = data['answers']
    assert question1['type'] == 'MEDIAN_LATENCY'
    assert question1['percentual_diff'] == 4900
    assert question1['median'] == request_1.duration
    assert question1['latencies_samples'] == {'baseline': [request_2.duration], 'comparison': [request_1.duration]}
    assert not question1['is_significant']
    assert question1['baseline_median'] == request_2.duration

    assert question2['type'] == 'STATUS_CODE_DISTRIBUTION'
    assert not question2['is_significant']
    assert question2['percentages'] is None


def test_make_report_post_is_significant(dashboard_user, endpoint, request_1, request_2, session):
    """TODO: implement this test."""
