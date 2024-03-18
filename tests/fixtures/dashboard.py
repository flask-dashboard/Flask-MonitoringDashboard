import pytest
import pytz
from flask import Flask

import flask_monitoringdashboard


@pytest.fixture
def config(colors=None, group_by=None):
    flask_monitoringdashboard.config.colors = colors or {'endpoint': '[0, 1, 2]'}
    flask_monitoringdashboard.config.group_by = group_by
    flask_monitoringdashboard.config.timezone = pytz.timezone('UTC')

    return flask_monitoringdashboard.config


@pytest.fixture
def view_func():
    return 'test'


@pytest.fixture
def dashboard(config, endpoint, view_func, rule='/'):
    print("inside dashboard...")
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    app.add_url_rule(rule, endpoint=endpoint.name, view_func=lambda: view_func)
    flask_monitoringdashboard.bind(app, schedule=False)


    with app.test_client() as client:
        yield client


@pytest.fixture
def dashboard_user(dashboard, user, config):
    """
    Returns a testing application that can be used for testing the endpoints.
    """
    dashboard.post('dashboard/login', data={'name': user.username, 'password': user.password})
    yield dashboard

    dashboard.post('dashboard/logout')


@pytest.fixture
def request_context(dashboard):
    with dashboard.application.test_request_context():
        yield
