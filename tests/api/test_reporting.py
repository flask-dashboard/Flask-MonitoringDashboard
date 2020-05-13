from datetime import datetime, timedelta
import pytest

from flask_monitoringdashboard.database import Endpoint


def test_make_report_get(dashboard_as_admin):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_as_admin.get('dashboard/api/reporting/make_report')
    assert not response.is_json


@pytest.mark.parametrize('request_1__time_requested', [datetime.utcnow() - timedelta(hours=6)])
@pytest.mark.parametrize('request_1__duration', [5000])
@pytest.mark.parametrize('request_1__status_code', [500])
@pytest.mark.parametrize('request_2__time_requested', [datetime.utcnow() - timedelta(days=1, hours=6)])
@pytest.mark.parametrize('request_2__duration', [100])
def test_make_report_post_not_significant(dashboard_as_admin, endpoint, request_1, request_2, session):
    response = dashboard_as_admin.post(
        'dashboard/api/reporting/make_report',
        json={
            'interval': {
                'from': (datetime.utcnow() - timedelta(days=1)).timestamp(),
                'to': datetime.utcnow().timestamp(),
            },
            'baseline_interval': {
                'from': (datetime.utcnow() - timedelta(days=2)).timestamp(),
                'to': (datetime.utcnow() - timedelta(days=1)).timestamp(),
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
