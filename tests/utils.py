"""
    Some useful functions for setting up the testing environment, adding data, etc..
"""
import datetime

from flask import Flask, json

from flask_monitoringdashboard.core.cache import EndpointInfo

NAME = 'main'
ENDPOINT_ID = 1
REQUEST_IDS = [1, 2, 3, 4, 5]
IP = '127.0.0.1'
GROUP_BY = '1'
REQUESTS = [1000, 2000, 3000, 4000, 50000]
BASE_OUTLIER_EXEC_TIME = 100
TIMES = [datetime.datetime.utcnow()] * 5
OUTLIER_COUNT = 3
for index, _ in enumerate(TIMES):
    TIMES[index] -= datetime.timedelta(seconds=len(REQUESTS) - index)
TEST_NAMES = ['test_name1', 'test_name2']
TEST_CACHE = {NAME: EndpointInfo()}


def set_test_environment():
    """ Override the config-object for a new testing environment. Module flask_monitoringdashboard
    must be imported locally. """
    import flask_monitoringdashboard

    flask_monitoringdashboard.config.database_name = 'sqlite:///test-database.db'


def clear_db():
    """ Drops and creates the tables in the database. Module flask_monitoringdashboard must be
    imported locally. """
    from flask_monitoringdashboard.database import get_tables, engine

    for table in get_tables():
        table.__table__.drop(engine)
        table.__table__.create(engine)


def add_fake_data():
    """ Adds data to the database for testing purposes. Module flask_monitoringdashboard must be
    imported locally. """
    from flask_monitoringdashboard.database import session_scope, Request, Endpoint, Outlier
    from flask_monitoringdashboard import config

    # Add requests
    with session_scope() as db_session:
        for i in range(len(REQUESTS)):
            call = Request(
                id=REQUEST_IDS[i],
                endpoint_id=ENDPOINT_ID,
                duration=REQUESTS[i],
                version_requested=config.version,
                time_requested=TIMES[i],
                group_by=GROUP_BY,
                ip=IP,
            )
            db_session.add(call)

        # Add endpoint
        db_session.add(
            Endpoint(
                id=ENDPOINT_ID,
                name=NAME,
                monitor_level=1,
                time_added=datetime.datetime.utcnow(),
                version_added=config.version,
                last_requested=TIMES[0],
            )
        )

        # Add Outliers
        for i in range(OUTLIER_COUNT):
            db_session.add(
                Outlier(request_id=i + 1, cpu_percent='[%d, %d, %d, %d]' % (i, i + 1, i + 2, i + 3))
            )


def get_test_app(schedule=False):
    """
    :return: Flask Test Application with the right settings
    """
    import flask_monitoringdashboard
    from flask import redirect, url_for

    user_app = Flask(__name__)

    @user_app.route('/')
    def main():
        return redirect(url_for('dashboard.index'))

    @user_app.route('/test_endpoint')
    def test_endpoint():
        return 'endpoint used for testing'

    user_app.config['SECRET_KEY'] = flask_monitoringdashboard.config.security_token
    user_app.testing = True
    flask_monitoringdashboard.user_app = user_app
    user_app.config['WTF_CSRF_ENABLED'] = False
    user_app.config['WTF_CSRF_METHODS'] = []
    flask_monitoringdashboard.config.get_group_by = lambda: '12345'
    flask_monitoringdashboard.bind(app=user_app, schedule=schedule)
    flask_monitoringdashboard.core.cache.memory_cache = TEST_CACHE
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
        headers = {'content-type': 'application/json'}

        test_case.assertEqual(
            204,
            c.post('dashboard/{}'.format(page), data=json.dumps(data), headers=headers).status_code,
        )
