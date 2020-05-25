import pytest

from flask_monitoringdashboard.core.colors import get_color


@pytest.mark.usefixtures('request_context')
def test_get_color():
    assert get_color('endpoint') == 'rgb(0, 1, 2)'
    assert get_color('main') in ['rgb(140, 191, 64)', 'rgb(140.0, 191.0, 64.0)']
