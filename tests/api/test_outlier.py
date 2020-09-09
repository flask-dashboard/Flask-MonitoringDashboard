import pytest


@pytest.mark.usefixtures('outlier_1', 'outlier_2')
def test_num_outliers(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/num_outliers/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    assert data == 2


@pytest.mark.parametrize('outlier_1__cpu_percent', ['[0, 1, 2, 3]'])
@pytest.mark.usefixtures('outlier_1')
def test_outlier_graph(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/outlier_graph/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    for i in range(4):
        assert data[i]['name'] == "CPU core {0}".format(i)
        assert data[i]['values'] == [i]


@pytest.mark.parametrize('outlier_1__cpu_percent', ['[0, 1, 2, 3]'])
@pytest.mark.parametrize('outlier_1__memory', ['memory'])
@pytest.mark.parametrize('outlier_1__request_environment', ['request_environment'])
@pytest.mark.parametrize('outlier_1__request_header', ['request_header'])
@pytest.mark.parametrize('outlier_1__request_url', ['request_url'])
@pytest.mark.parametrize('outlier_1__stacktrace', ['stacktrace'])
@pytest.mark.parametrize('offset,per_page', [[0, 10]])
def test_outlier_table(dashboard_user, outlier_1, endpoint, offset, per_page):
    response = dashboard_user.get(
        'dashboard/api/outlier_table/{0}/{1}/{2}'.format(endpoint.id, offset, per_page),
    )
    assert response.status_code == 200

    [data] = response.json
    assert data['cpu_percent'] == outlier_1.cpu_percent
    assert data['id'] == str(outlier_1.id)
    assert data['memory'] == outlier_1.memory
    assert data['request_id'] == str(outlier_1.request.id)
    assert data['request_environment'] == outlier_1.request_environment
    assert data['request_header'] == outlier_1.request_header
    assert data['request_url'] == outlier_1.request_url
    assert data['stacktrace'] == outlier_1.stacktrace
