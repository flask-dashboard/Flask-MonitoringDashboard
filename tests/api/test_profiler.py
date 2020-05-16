import pytest

from flask_monitoringdashboard.core.timezone import to_local_datetime


@pytest.mark.usefixtures('stack_line', 'stack_line_2')
def test_num_profiled(dashboard_user, endpoint):
    response = dashboard_user.get('dashboard/api/num_profiled/{0}'.format(endpoint.id))
    assert response.status_code == 200

    data = response.json
    assert data == 2


@pytest.mark.parametrize('request_1__group_by', ['group_by'])
@pytest.mark.parametrize('offset,per_page', [[0, 10]])
def test_profiler_table(dashboard_user, stack_line, request_1, endpoint, offset, per_page):
    response = dashboard_user.get(
        'dashboard/api/profiler_table/{0}/{1}/{2}'.format(endpoint.id, offset, per_page),
    )
    assert response.status_code == 200

    [data] = response.json
    assert data['duration'] == str(request_1.duration)
    assert data['endpoint_id'] == str(endpoint.id)
    assert data['group_by'] == request_1.group_by
    assert data['id'] == str(request_1.id)
    assert data['ip'] == request_1.ip
    assert data['status_code'] == str(request_1.status_code)
    assert data['time_requested'] == str(to_local_datetime(request_1.time_requested))
    assert data['version_requested'] == request_1.version_requested

    assert len(data['stack_lines']) == 1
    assert data['stack_lines'][0]['code']['code'] == stack_line.code.code
    assert data['stack_lines'][0]['code']['filename'] == stack_line.code.filename
    assert data['stack_lines'][0]['code']['function_name'] == stack_line.code.function_name
    assert data['stack_lines'][0]['code']['line_number'] == str(stack_line.code.line_number)


def test_grouped_profiler(dashboard_user, stack_line, endpoint):
    response = dashboard_user.get('dashboard/api/grouped_profiler/{0}'.format(endpoint.id))
    assert response.status_code == 200

    [data] = response.json
    assert data['code'] == stack_line.code.code
    assert data['duration'] == stack_line.duration
    assert data['hits'] == 1
    assert data['indent'] == stack_line.indent
    assert data['std'] == 0
    assert data['total_hits'] == 1
