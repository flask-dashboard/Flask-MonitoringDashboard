from datetime import datetime

import pytest


@pytest.mark.parametrize('request_1__time_requested', [datetime(2020, 1, 1)])
def test_versions(dashboard_user, request_1):
    response = dashboard_user.get('dashboard/api/versions')

    assert response.status_code == 200

    [data] = [row for row in response.json if row['version'] == request_1.version_requested]
    assert data['date'] == request_1.time_requested.strftime("%a, %d %b %Y %H:%M:%S GMT")


@pytest.mark.parametrize('request_1__time_requested', [datetime(2020, 1, 1)])
def test_versions_for_endpoint(dashboard_user, request_1, endpoint):
    response = dashboard_user.get('dashboard/api/versions/{0}'.format(endpoint.id))

    assert response.status_code == 200

    [data] = response.json

    assert data == {
        'version': request_1.version_requested,
        'date': request_1.time_requested.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    }


def test_multi_version_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/multi_version')
    assert not response.is_json


def test_multi_version_post(dashboard_user, request_1, request_2, endpoint):
    response = dashboard_user.post('dashboard/api/multi_version', json={'data': {
        'endpoints': [endpoint.name],
        'versions': [request_1.version_requested, request_2.version_requested],
    }})
    assert response.status_code == 200

    data = response.json
    assert data == [[100, 100]]


def test_version_user_get(dashboard_user, endpoint):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/version_user/{0}'.format(endpoint.id))
    assert not response.is_json


@pytest.mark.parametrize('request_1__group_by', ['a'])
@pytest.mark.parametrize('request_2__group_by', ['b'])
def test_version_user_post(dashboard_user, request_1, request_2, endpoint):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.post('dashboard/api/version_user/{0}'.format(endpoint.id), json={'data': {
        'users': ['a', 'b'],
        'versions': [request_1.version_requested, request_2.version_requested],
    }})
    assert response.status_code == 200
    data = response.json

    assert data['data'] == [[request_1.duration, 0], [0, request_2.duration]]

    for index, request in enumerate([request_1, request_2]):
        assert data['versions'][index] == {
            'date': request.time_requested.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'version': request.version_requested,
        }


def test_version_ip_get(dashboard_user, endpoint):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/version_ip/{0}'.format(endpoint.id))
    assert not response.is_json


@pytest.mark.parametrize('request_1__ip', ['127.0.0.1'])
@pytest.mark.parametrize('request_2__ip', ['127.0.0.2'])
def test_version_ip_post(dashboard_user, request_1, request_2, endpoint):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.post('dashboard/api/version_ip/{0}'.format(endpoint.id), json={'data': {
        'ip': ['127.0.0.1', '127.0.0.2'],
        'versions': [request_1.version_requested, request_2.version_requested],
    }})
    assert response.status_code == 200
    data = response.json

    assert data['data'] == [[request_1.duration, 0], [0, request_2.duration]]

    for index, request in enumerate([request_1, request_2]):
        assert data['versions'][index] == {
            'date': request.time_requested.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'version': request.version_requested,
        }