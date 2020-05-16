from datetime import datetime

import pytest


@pytest.mark.parametrize('request_1__time_requested', [datetime(2020, 1, 1)])
@pytest.mark.parametrize('request_2__time_requested', [datetime(2020, 1, 2)])
@pytest.mark.usefixtures('request_1', 'request_2')
def test_num_requests(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/requests/2020-01-01/2020-01-02')

    assert response.status_code == 200

    assert response.json['days'] == ['2020-01-01', '2020-01-02']
    [data] = [row for row in response.json['data'] if row['name'] == endpoint.name]
    assert data['values'] == [1, 1]


@pytest.mark.parametrize('request_1__time_requested', [datetime(2020, 1, 1, hour=2)])
@pytest.mark.parametrize('request_2__time_requested', [datetime(2020, 1, 1, hour=3)])
@pytest.mark.usefixtures('request_1', 'request_2')
def test_hourly_load(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/hourly_load/2020-01-01/2020-01-01/{0}'.format(endpoint.id))

    assert response.status_code == 200

    data = response.json
    assert data['days'] == ['2020-01-01']
    for index, row in enumerate(data['data']):
        if index in [2, 3]:
            assert row == [1]
        else:
            assert row == [0]

