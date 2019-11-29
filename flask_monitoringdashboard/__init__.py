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
from flask_monitoringdashboard.core.logger import log

config = Config()


# get current location of the project
def loc():
    return os.path.abspath(os.path.dirname(__file__)) + '/'


# define the blueprint
blueprint = Blueprint('dashboard', __name__, template_folder=loc() + 'templates')


def bind(app, schedule=True):
    """
        Binding the app to this object should happen before importing the routing-
        methods below. Thus, the importing statement is part of this function.
        :param app: the app for which the performance has to be tracked
        :param schedule: flag telling if the background scheduler should be started
    """
    config.app = app
    # Provide a secret-key for using WTF-forms
    if not app.secret_key:
        log('WARNING: You should provide a security key.')
        app.secret_key = 'my-secret-key'

    # Add all route-functions to the blueprint
    from flask_monitoringdashboard.views import (
        deployment,
        custom,
        endpoint,
        outlier,
        request,
        profiler,
        version,
        auth,
        reporting,
    )
    import flask_monitoringdashboard.views

    # Add wrappers to the endpoints that have to be monitored
    from flask_monitoringdashboard.core.measurement import init_measurement
    from flask_monitoringdashboard.core.cache import init_cache
    from flask_monitoringdashboard.core import custom_graph

    blueprint.before_app_first_request(init_measurement)
    blueprint.before_app_first_request(init_cache)
    if schedule:
        custom_graph.init(app)

    # register the blueprint to the app
    app.register_blueprint(blueprint, url_prefix='/' + config.link)

    # flush cache to db before shutdown
    import atexit
    from flask_monitoringdashboard.core.cache import flush_cache

    atexit.register(flush_cache)


def add_graph(title, func, trigger="interval", **schedule):
    """
    Add a custom graph to the dashboard. You must specify the following arguments
    :param title: title of the graph (must be unique)
    :param schedule: dict containing values for weeks, days, hours, minutes, seconds
    :param func: function reference without arguments
    :param trigger: str|apscheduler.triggers.base.BaseTrigger trigger: trigger that determines when
            ``func`` is called
    """
    from flask_monitoringdashboard.core import custom_graph

    graph_id = custom_graph.register_graph(title)
    custom_graph.add_background_job(func, graph_id, trigger, **schedule)
