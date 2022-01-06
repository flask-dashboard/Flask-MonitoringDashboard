import pytest
import pytz
import os
from flask import Flask
from flask_monitoringdashboard.database import DatabaseConnectionWrapper
import flask_monitoringdashboard


@pytest.fixture
def config(colors=None, group_by=None):
    flask_monitoringdashboard.config.colors = colors or {'endpoint': '[0, 1, 2]'}
    flask_monitoringdashboard.config.group_by = group_by
    flask_monitoringdashboard.config.timezone = pytz.timezone('UTC')
    if os.environ.get("MONGO_DB") == "true":
        print("RUNNING ON MONGODB")
        flask_monitoringdashboard.config.database_name = "mongodb://localhost:27017,localhost:37017,localhost:47017/flask_monitoringdashboard"
    DatabaseConnectionWrapper(flask_monitoringdashboard.config)
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
