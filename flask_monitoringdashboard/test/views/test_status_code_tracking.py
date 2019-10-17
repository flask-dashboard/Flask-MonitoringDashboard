import unittest
from time import sleep

from flask import Flask, json, jsonify
from flask_monitoringdashboard.core.cache import EndpointInfo
from flask_monitoringdashboard.database import session_scope, Request

from flask_monitoringdashboard.test.utils import (
    set_test_environment,
    clear_db
)


def get_test_app_for_status_code_testing(schedule=False):
    """
    :return: Flask Test Application with the right settings
    """
    import flask_monitoringdashboard

    app = Flask(__name__)

    @app.route('/return-a-simple-string')
    def return_a_simple_string():
        return 'Hello, world'

    @app.route('/return-a-tuple')
    def return_a_tuple():
        return 'Hello, world', 404

    @app.route('/ridiculous-return-value')
    def return_ridiculous_return_value():
        return 'hello', 'ridiculous'

    @app.route('/return-jsonify-default-status-code')
    def return_jsonify_default_status_code():
        return jsonify({
            'apples': 'banana'
        })

    @app.route('/return-jsonify-with-custom-status-code')
    def return_jsonify_with_custom_status_code():
        response = jsonify({
            'cheese': 'pears'
        })
        response.status_code = 401
        return response

    @app.route('/unhandled-exception')
    def unhandled_exception():
        potatoes = 1000
        bananas = 0

        return potatoes / bananas

    app.config['SECRET_KEY'] = flask_monitoringdashboard.config.security_token
    app.testing = True
    flask_monitoringdashboard.user_app = app
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_METHODS'] = []
    flask_monitoringdashboard.config.get_group_by = lambda: '12345'
    flask_monitoringdashboard.bind(app=app, schedule=schedule)
    TEST_CACHE = {'main': EndpointInfo()}
    flask_monitoringdashboard.core.cache.memory_cache = TEST_CACHE
    return app


class TestLogin(unittest.TestCase):
    def setUp(self):
        set_test_environment()
        clear_db()
        self.app = get_test_app_for_status_code_testing()

    def test_simple_string_response(self):
        """
            An endpoint that just returns a string yields a HTTP 200 status code and should be logged as such.
        """
        with self.app.test_client() as c:
            c.get('/return-a-simple-string')

            with session_scope() as db_session:
                requests = db_session.query(Request.status_code).all()

                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0][0], 200)

    def test_return_a_tuple(self):
        """
        An endpoint that returns a tuple should log the second parameter as status_code
        """
        with self.app.test_client() as c:
            c.get('/return-a-tuple')

            with session_scope() as db_session:
                requests = db_session.query(Request.status_code, Request.endpoint_id).all()

                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0][0], 404)

    def test_jsonify_default_status_code(self):
        """
        An endpoint that returns a Response as a return value of jsonify without setting the status_cod yields a HTTP
        200 status and should be logged as such.
        """
        with self.app.test_client() as c:
            c.get('/return-jsonify-default-status-code')

            with session_scope() as db_session:
                requests = db_session.query(Request.status_code, Request.endpoint_id).all()

                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0][0], 200)

    def test_jsonify_with_custom_status_code(self):
        """
        An endpoint that returns a Response and has a custom status code assigned should properly log the specified
        status code
        """
        with self.app.test_client() as c:
            c.get('/return-jsonify-with-custom-status-code')

            with session_scope() as db_session:
                requests = db_session.query(Request.status_code, Request.endpoint_id).all()

                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0][0], 401)

    def test_ridiculous_return_value(self):
        """
        An endpoint that returns a silly status code like a string should yield a 500 status code
        """
        with self.app.test_client() as c:
            c.get('/ridiculous-return-value')

            with session_scope() as db_session:
                requests = db_session.query(Request.status_code, Request.endpoint_id).all()

                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0][0], 500)

    def test_unhandled_exception(self):
        """
        An endpoint that returns a silly status code like a string should yield a 500 status code
        """
        with self.app.test_client() as c:
            try:
                c.get('/unhandled-exception')
            except:
                pass

            sleep(.5)

            with session_scope() as db_session:
                requests = db_session.query(Request.status_code, Request.endpoint_id).all()

                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0][0], 500)
