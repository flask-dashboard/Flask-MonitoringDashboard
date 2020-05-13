import pytest

from flask_monitoringdashboard.core.auth import check_login


@pytest.mark.usefixtures('request_context')
def test_check_login(config):
    """Test if function 'check_login' works."""
    assert check_login(config.username, config.password)
    assert check_login(config.guest_username, config.guest_password[0])


@pytest.mark.usefixtures('request_context')
def test_check_login_should_fail(config):
    """Test if function 'check_login' works."""
    assert not check_login('incorrect', config.password)
    assert not check_login(config.username, 'incorrect')
    assert not check_login('incorrect', config.guest_password)
    assert not check_login(config.guest_username, 'incorrect')
