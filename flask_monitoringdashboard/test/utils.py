"""
    Some useful functions for setting up the testing environment, adding data, etc..
"""
import datetime

from flask import Flask

NAME = 'main'
IP = '127.0.0.1'
GROUP_BY = '1'
EXECUTION_TIMES = [1000, 2000, 3000, 4000, 50000]
TIMES = [datetime.datetime.now()] * 5
for i in range(len(TIMES)):
    TIMES[i] += datetime.timedelta(seconds=i)
TEST_NAMES = ['test_name1', 'test_name2']


def set_test_environment():
    """ Override the config-object for a new testing environment. Module dashboard must be imported locally. """
    import flask_monitoringdashboard
    flask_monitoringdashboard.config.database_name = 'sqlite:///test-database.db'


def clear_db():
    """ Drops and creates the tables in the database. Module dashboard must be imported locally. """
    from flask_monitoringdashboard.database import get_tables, engine
    for table in get_tables():
        table.__table__.drop(engine)
        table.__table__.create(engine)


def add_fake_data():
    """ Adds data to the database for testing purposes. Module dashboard must be imported locally. """
    from flask_monitoringdashboard.database import session_scope, FunctionCall, MonitorRule, Tests, TestsGrouped
    from flask_monitoringdashboard import config

    # Add functionCalls
    with session_scope() as db_session:
        for i in range(len(EXECUTION_TIMES)):
            call = FunctionCall(endpoint=NAME, execution_time=EXECUTION_TIMES[i], version=config.version,
                                time=TIMES[i], group_by=GROUP_BY, ip=IP)
            db_session.add(call)

    # Add MonitorRule
    with session_scope() as db_session:
        db_session.add(MonitorRule(endpoint=NAME, monitor=True, time_added=datetime.datetime.now(),
                                   version_added=config.version, last_accessed=TIMES[0]))

    # Add Tests
    with session_scope() as db_session:
        db_session.add(Tests(name=NAME, succeeded=True))

    # Add TestsGrouped
    with session_scope() as db_session:
        for test_name in TEST_NAMES:
            db_session.add(TestsGrouped(endpoint=NAME, test_name=test_name))


def get_test_app():
    """
    :return: Flask Test Application with the right settings
    """
    import flask_monitoringdashboard
    user_app = Flask(__name__)
    user_app.config['SECRET_KEY'] = flask_monitoringdashboard.config.security_token
    user_app.testing = True
    flask_monitoringdashboard.config.get_group_by = lambda: '12345'
    flask_monitoringdashboard.bind(app=user_app)
    return user_app.test_client()


def login(test_app):
    """
    Used for setting the sessions, such that you have a fake login to the dashboard.
    :param test_app:
    """
    from flask_monitoringdashboard import config
    with test_app as c:
        with c.session_transaction() as sess:
            sess[config.link + '_logged_in'] = True
            sess[config.link + '_admin'] = True


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)
