"""
    Some useful functions for setting up the testing environment, adding data, etc..
"""
import datetime

from flask import Flask

NAME = 'main'
IP = '127.0.0.1'
GROUP_BY = '1'
EXECUTION_TIMES = [1000, 2000, 3000, 4000, 50000]
BASE_OUTLIER_EXEC_TIME = 100
TIMES = [datetime.datetime.utcnow()] * 5
OUTLIER_COUNT = 3
for i in range(len(TIMES)):
    TIMES[i] -= datetime.timedelta(seconds=len(EXECUTION_TIMES) - i)
TEST_NAMES = ['test_name1', 'test_name2']


def set_test_environment():
    """ Override the config-object for a new testing environment. Module flask_monitoringdashboard
    must be imported locally. """
    import flask_monitoringdashboard
    flask_monitoringdashboard.config.database_name = 'sqlite:///test-database.db'


def clear_db():
    """ Drops and creates the tables in the database. Module flask_monitoringdashboard must be imported locally. """
    from flask_monitoringdashboard.database import get_tables, engine
    for table in get_tables():
        table.__table__.drop(engine)
        table.__table__.create(engine)


def add_fake_data():
    """ Adds data to the database for testing purposes. Module flask_monitoringdashboard must be imported locally. """
    from flask_monitoringdashboard.database import session_scope, FunctionCall, MonitorRule, Outlier, TestsGrouped
    from flask_monitoringdashboard import config

    # Add functionCalls
    with session_scope() as db_session:
        for i in range(len(EXECUTION_TIMES)):
            call = FunctionCall(endpoint=NAME, execution_time=EXECUTION_TIMES[i], version=config.version,
                                time=TIMES[i], group_by=GROUP_BY, ip=IP)
            db_session.add(call)

    # Add MonitorRule
    with session_scope() as db_session:
        db_session.add(MonitorRule(endpoint=NAME, monitor=True, time_added=datetime.datetime.utcnow(),
                                   version_added=config.version, last_accessed=TIMES[0]))

    # Add Outliers
    with session_scope() as db_session:
        for i in range(OUTLIER_COUNT):
            db_session.add(Outlier(endpoint=NAME, cpu_percent='[%d, %d, %d, %d]' % (i, i + 1, i + 2, i + 3),
                                   execution_time=BASE_OUTLIER_EXEC_TIME * (i + 1), time=TIMES[i]))

    # Add TestsGrouped
    with session_scope() as db_session:
        for test_name in TEST_NAMES:
            db_session.add(TestsGrouped(endpoint=NAME, test_name=test_name))


def add_fake_test_runs():
    """ Adds test run data to the database for testing purposes. """
    from flask_monitoringdashboard.database import session_scope, TestRun
    from flask_monitoringdashboard import config

    with session_scope() as db_session:
        for test_name in TEST_NAMES:
            for i in range(len(EXECUTION_TIMES)):
                db_session.add(
                    TestRun(name=test_name, execution_time=EXECUTION_TIMES[i], time=datetime.datetime.utcnow(),
                            version=config.version, suite=1, run=i))


def get_test_app():
    """
    :return: Flask Test Application with the right settings
    """
    import flask_monitoringdashboard
    from flask import redirect, url_for
    user_app = Flask(__name__)

    @user_app.route('/')
    def main():
        return redirect(url_for('dashboard.index'))

    user_app.config['SECRET_KEY'] = flask_monitoringdashboard.config.security_token
    user_app.testing = True
    flask_monitoringdashboard.user_app = user_app
    user_app.config['WTF_CSRF_ENABLED'] = False
    user_app.config['WTF_CSRF_METHODS'] = []
    flask_monitoringdashboard.config.get_group_by = lambda: '12345'
    flask_monitoringdashboard.bind(app=user_app)
    return user_app


def login(test_app):
    """
    Used for setting the sessions, such that you have a fake login to the flask_monitoringdashboard.
    :param test_app:
    """
    from flask_monitoringdashboard import config
    with test_app.session_transaction() as sess:
        sess[config.link + '_logged_in'] = True
        sess[config.link + '_admin'] = True


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def test_admin_secure(test_case, page):
    """
    Test whether the page is only accessible with admin credentials.
    :param test_case: test class, must be an instance of unittest.TestCase
    :param page: str with the page of the flask_monitoringdashboard
    """
    with test_case.app.test_client() as c:
        test_case.assertEqual(302, c.get('dashboard/{}'.format(page)).status_code)
        login(c)
        test_case.assertEqual(200, c.get('dashboard/{}'.format(page)).status_code)


def test_get_redirect(test_case, page):
    """
    Test whether the page returns a redirection.
    :param test_case: test class, must be an instance of unittest.TestCase
    :param page: str with the page of the flask_monitoringdashboard
    """
    with test_case.app.test_client() as c:
        test_case.assertEqual(302, c.get('dashboard/{}'.format(page)).status_code)


def test_get_ok(test_case, page):
    """
    Test whether the page returns a 200 OK.
    :param test_case: test class, must be an instance of unittest.TestCase
    :param page: str with the page of the flask_monitoringdashboard
    """
    with test_case.app.test_client() as c:
        test_case.assertEqual(200, c.get('dashboard/{}'.format(page)).status_code)


def test_post_data(test_case, page, data):
    """
    Test whether a post request can successfully be made to the page.
    :param test_case: test class, must be an instance of unittest.TestCase
    :param page: str with the page of the flask_monitoringdashboard
    :param data: the data that should be posted to the page
    """
    with test_case.app.test_client() as c:
        test_case.assertEqual(204, c.post('dashboard/{}'.format(page), json=data).status_code)
