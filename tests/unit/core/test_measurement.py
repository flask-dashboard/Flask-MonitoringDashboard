import pytest

from flask_monitoringdashboard.core.measurement import init_measurement, add_decorator


@pytest.mark.usefixtures('request_context')
def test_init_measurement():
    init_measurement()


@pytest.mark.usefixtures('request_context')
@pytest.mark.parametrize('endpoint__monitor_level', [0, 1, 2, 3])
def test_add_decorator(endpoint, config):
    def f():
        pass

    config.app.view_functions[endpoint.name] = f
    add_decorator(endpoint)
    assert config.app.view_functions[endpoint.name].original == f


@pytest.mark.usefixtures('request_context')
@pytest.mark.parametrize('endpoint__monitor_level', [-1])
def test_add_decorator_fails(endpoint, config):
    config.app.view_functions[endpoint.name] = lambda: 42
    with pytest.raises(ValueError):
        endpoint.monitor_level = -1
        add_decorator(endpoint)
