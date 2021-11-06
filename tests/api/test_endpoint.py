import pytest

from flask_monitoringdashboard.database import Endpoint, Request


@pytest.mark.parametrize('endpoint__monitor_level', [3])
def test_overview(dashboard_user, request_1, request_2, endpoint, session):
    response = dashboard_user.get('dashboard/api/overview')
    assert response.status_code == 200

    [data] = [row for row in response.json if row['id'] == endpoint.id]

    assert data['hits-overall'] == 2
    assert data['hits-today'] == 2
    assert data['hits-today-errors'] == 0
    assert data['hits-week'] == 2
    assert data['hits-week-errors'] == 0

    assert data['last-accessed'] == endpoint.last_requested.strftime("%a, %d %b %Y %H:%M:%S GMT")

    assert data['median-overall'] == (request_1.duration + request_2.duration) / 2
    assert data['median-today'] == (request_1.duration + request_2.duration) / 2
    assert data['median-week'] == (request_1.duration + request_2.duration) / 2

    assert data['monitor'] == 3
    assert data['name'] == endpoint.name
    assert data['blueprint'] == endpoint.name


@pytest.mark.parametrize('request_1__group_by', ['42'])
@pytest.mark.parametrize('request_2__group_by', ['something else'])
@pytest.mark.usefixtures('request_1', 'request_2')
def test_users(dashboard_user, endpoint, session):
    response = dashboard_user.get('dashboard/api/users/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    row1, row2 = data

    assert row1['hits'] == 1
    assert row1['user'] == '42' or 'something else'
    assert row2['hits'] == 1
    assert row2['user'] == '42' or 'something else'


@pytest.mark.parametrize('request_1__ip', ['42'])
@pytest.mark.parametrize('request_2__ip', ['something else'])
@pytest.mark.usefixtures('request_1', 'request_2')
def test_ips(dashboard_user, endpoint, session):
    response = dashboard_user.get('dashboard/api/ip/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    row1, row2 = data

    assert row1['hits'] == 1
    assert row1['ip'] == '42' or 'something else'
    assert row2['hits'] == 1
    assert row2['ip'] == '42' or 'something else'


def test_endpoints(dashboard_user, endpoint, session):
    response = dashboard_user.get('dashboard/api/endpoints')
    assert response.status_code == 200

    assert len(response.json) == session.query(Endpoint).count()
    [data] = [row for row in response.json if row['id'] == str(endpoint.id)]

    assert data['last_requested'] == str(endpoint.last_requested)
    assert data['monitor_level'] == str(endpoint.monitor_level)
    assert data['name'] == endpoint.name
    assert data['time_added'] == str(endpoint.time_added)
    assert data['version_added'] == endpoint.version_added


@pytest.mark.usefixtures('request_1', 'request_2')
def test_endpoint_hits(dashboard_user, endpoint, session):
    response = dashboard_user.get('dashboard/api/endpoints_hits')
    assert response.status_code == 200

    total_hits = sum(row['hits'] for row in response.json)
    assert total_hits == session.query(Request).count()

    [data] = [row for row in response.json if row['name'] == endpoint.name]
    assert data['hits'] == 2


def test_api_performance_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/api_performance')
    assert not response.is_json


def test_api_performance_post(dashboard_user, request_1, endpoint, session):
    response = dashboard_user.post('dashboard/api/api_performance', json={
        'data': {'endpoints': [endpoint.name]}
    })

    assert response.status_code == 200
    [data] = response.json
    assert data['values'] == [request_1.duration]


def test_set_rule_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/set_rule')
    assert not response.is_json


@pytest.mark.parametrize('user__is_admin', [False])
def test_set_rule_post_guest_not_allowed(dashboard_user, endpoint):
    """Guest is redirected to the login page."""
    response = dashboard_user.post('dashboard/api/set_rule', data={
        'name': endpoint.name,
        'value': 3,
    })
    assert response.status_code == 302


@pytest.mark.parametrize('endpoint__monitor_level', [1])
def test_set_rule_post(dashboard_user, endpoint, session):
    response = dashboard_user.post('dashboard/api/set_rule', data={
        'name': endpoint.name,
        'value': 3,
    })

    assert response.status_code == 200
    assert response.data == b'OK'
    endpoint = session.query(Endpoint).get(endpoint.id)  # reload the endpoint
    assert endpoint.monitor_level == 3


@pytest.mark.usefixtures('request_1')
def test_endpoint_info(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/endpoint_info/{0}'.format(endpoint.id))
    assert response.status_code == 200
    data = response.json

    assert data['endpoint'] == endpoint.name
    assert data['monitor-level'] == endpoint.monitor_level
    assert data['total_hits'] == 1
    assert data['rules'] == ['/']
    assert data['url'] == '/'


@pytest.mark.parametrize('request_1__status_code', [404])
@pytest.mark.parametrize('request_2__status_code', [200])
@pytest.mark.usefixtures('request_1', 'request_2')
def test_endpoint_status_code_distribution(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/endpoint_status_code_distribution/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    assert data['200'] == 1 / 2
    assert data['404'] == 1 / 2


@pytest.mark.parametrize('request_1__status_code', [404])
@pytest.mark.parametrize('request_2__status_code', [200])
@pytest.mark.usefixtures('request_2')
def test_endpoint_status_code_summary(dashboard_user, request_1, endpoint):
    response = dashboard_user.get('dashboard/api/endpoint_status_code_summary/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    assert data['distribution'] == {'200': 1 / 2, '404': 1 / 2}
    [row] = data['error_requests']

    assert row['duration'] == str(request_1.duration)
    assert row['endpoint_id'] == str(endpoint.id)
    assert row['group_by'] == str(request_1.group_by)
    assert row['id'] == str(request_1.id)
    assert row['ip'] == request_1.ip
    assert row['time_requested'] == str(request_1.time_requested)
    assert row['version_requested'] == request_1.version_requested


def test_endpoint_versions_get(dashboard_user, endpoint):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/endpoint_versions/{0}'.format(endpoint.id))
    assert not response.is_json


@pytest.mark.parametrize('request_1__version_requested', ['a'])
@pytest.mark.parametrize('request_2__version_requested', ['b'])
def test_endpoint_versions_post(dashboard_user, request_1, request_2, endpoint):
    response = dashboard_user.post(
        'dashboard/api/endpoint_versions/{0}'.format(endpoint.id),
        json={'data': {'versions': [request_1.version_requested, request_2.version_requested]}},
    )
    assert response.status_code == 200
    row1, row2 = response.json

    assert row1['version'] == request_1.version_requested
    assert row1['values'] == [request_1.duration]

    assert row2['version'] == request_2.version_requested
    assert row2['values'] == [request_2.duration]


def test_endpoint_users_get(dashboard_user, endpoint):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/endpoint_users/{0}'.format(endpoint.id))
    assert not response.is_json


@pytest.mark.parametrize('request_1__group_by', ['a'])
@pytest.mark.parametrize('request_2__group_by', ['b'])
def test_endpoint_users_post(dashboard_user, request_1, request_2, endpoint):
    response = dashboard_user.post(
        'dashboard/api/endpoint_users/{0}'.format(endpoint.id),
        json={'data': {'users': [request_1.group_by, request_2.group_by]}},
    )
    assert response.status_code == 200
    row1, row2 = response.json

    assert row1['user'] == request_1.group_by
    assert row1['values'] == [request_1.duration]

    assert row2['user'] == request_2.group_by
    assert row2['values'] == [request_2.duration]