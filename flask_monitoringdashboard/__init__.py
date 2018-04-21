"""
    The app tracks the performance of various endpoints over time.
    To bind, use the following lines of code:
        import dashboard
        from flask import Flask
        ...
        app = Flask(__name__)
        ...
        dashboard.bind(app)

    The dashboard with the results that are collected can be found at:
        localhost:5000/dashboard
"""

import os

from flask import Blueprint

from flask_monitoringdashboard.core.config import Config

config = Config()
user_app = None


# get current location of the project
def loc():
    return os.path.abspath(os.path.dirname(__file__)) + '/'


# define the blueprint
blueprint = Blueprint('dashboard', __name__, template_folder=loc() + 'templates')


def bind(app, blue_print=None):
    """
        Binding the app to this object should happen before importing the routing-
        methods below. Thus, the importing statement is part of this function.
        :param app: the app for which the performance has to be tracked
        :param blue_print: the blueprint that contains the endpoints to be monitored
    """
    assert app is not None
    global user_app, blueprint
    user_app = app

    # Provide a secret-key for using WTF-forms
    if not user_app.secret_key:
        print('WARNING: You should provide a security key.')
        user_app.secret_key = 'my-secret-key'

    if blue_print:
        import os
        import datetime
        from flask import request

        @blue_print.after_request
        def after_request(response):
            hit_time_stamp = str(datetime.datetime.now())
            log = open("endpoint_hits.log", "a")
            log.write('"{}","{}"\n'.format(hit_time_stamp, request.endpoint))
            log.close()
            return response

    # Add all route-functions to the blueprint
    import flask_monitoringdashboard.views

    # Add wrappers to the endpoints that have to be monitored
    from flask_monitoringdashboard.core.measurement import init_measurement
    blueprint.before_app_first_request(init_measurement)

    # register the blueprint to the app
    app.register_blueprint(blueprint, url_prefix='/' + config.link)
