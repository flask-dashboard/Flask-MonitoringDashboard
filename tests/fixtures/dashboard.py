import pytest
from flask import Flask

import flask_monitoringdashboard


@pytest.fixture
def config(username='admin', password='admin', guest_username=None, guest_password=None, colors=None, group_by=None):
    flask_monitoringdashboard.config.username = username
    flask_monitoringdashboard.config.password = password
    flask_monitoringdashboard.config.guest_username = guest_username or 'guest'
    flask_monitoringdashboard.config.guest_password = guest_password or ['guest_password']
    flask_monitoringdashboard.config.colors = colors or {'endpoint': '[0, 1, 2]'}
    flask_monitoringdashboard.config.group_by = group_by

    return flask_monitoringdashboard.config


@pytest.fixture
def view_func():
    return 'test'


@pytest.fixture
def dashboard(config, endpoint, view_func, rule='/'):
    app = Flask(__name__)
    app.add_url_rule(rule, endpoint=endpoint.name, view_func=lambda: view_func)
    flask_monitoringdashboard.bind(app, schedule=False)

    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def is_admin():
    """Set to True for testing as an admin."""
    return False


@pytest.fixture
def dashboard_user(dashboard, is_admin, config):
    """
    Returns a testing application that can be used for testing the endpoints.
    If is_admin is False, the guest is logged into the dashboard.
    """
    if is_admin:
        dashboard.post('dashboard/login', data={'name': config.username, 'password': config.password})
    else:
        dashboard.post('dashboard/login', data={'name': config.guest_username, 'password': config.guest_password[0]})
    yield dashboard

    dashboard.post('dashboard/logout')


@pytest.fixture
def request_context(dashboard):
    with dashboard.application.test_request_context():
        yield
