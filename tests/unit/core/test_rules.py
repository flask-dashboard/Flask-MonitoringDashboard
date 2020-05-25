import pytest
from flask_monitoringdashboard.core.rules import get_rules


@pytest.mark.usefixtures('request_context')
def test_rules(endpoint):
    assert len(get_rules()) == 1
    assert len(get_rules(endpoint.name)) == 1
    assert get_rules('unknown') == []
