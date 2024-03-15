"""The app tracks the performance of various endpoints over time.
To bind, use the following lines of code:

>>> import flask_monitoringdashboard as dashboard
>>> from flask import Flask
    ...
>>> app = Flask(__name__)
    ...
>>> dashboard.bind(app)

The dashboard with the results that are collected can be found at:
    localhost:5000/dashboard
"""

import os

from flask import Blueprint

from flask_monitoringdashboard.core.config import Config, TelemetryConfig
from flask_monitoringdashboard.core.logger import log


def loc():
    """Get the current location of the project."""
    return os.path.abspath(os.path.dirname(__file__)) + '/'


config = Config()
telemetry_config = TelemetryConfig()
blueprint = Blueprint('dashboard', __name__, template_folder=loc() + 'templates')


def bind(app, schedule=True, include_dashboard=True):
    """Binding the app to this object should happen before importing the routing-
    methods below. Thus, the importing statement is part of this function.

    :param app: the app for which the performance has to be tracked
    :param schedule: flag telling if the background scheduler should be started
    :param include_dashboard: flag telling if the views should be added or not.
    """
    blueprint.name = config.blueprint_name
    config.app = app
    # Provide a secret-key for using WTF-forms
    if not app.secret_key:
        log('WARNING: You should provide a security key.')
        app.secret_key = 'my-secret-key'

    # Add all route-functions to the blueprint
    if include_dashboard:
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
            telemetry,
            pruning
        )
        import flask_monitoringdashboard.views

    # Add wrappers to the endpoints that have to be monitored
    from flask_monitoringdashboard.core.measurement import init_measurement
    from flask_monitoringdashboard.core.cache import init_cache
    from flask_monitoringdashboard.core import custom_graph

    blueprint.record_once(lambda _state: init_measurement())
    blueprint.record_once(lambda _state: init_cache())
    if schedule:
        custom_graph.init(app)

    # register the blueprint to the app
    app.register_blueprint(blueprint, url_prefix='/' + config.link)

    # flush cache to db before shutdown
    import atexit
    from flask_monitoringdashboard.core.cache import flush_cache

    atexit.register(flush_cache)

    if not include_dashboard:
        @app.teardown_request
        def teardown(_):
            flush_cache()


def add_graph(title, func, trigger="interval", **schedule):
    """Add a custom graph to the dashboard. You must specify the following arguments:

    :param title: title of the graph (must be unique)
    :param schedule: dict containing values for weeks, days, hours, minutes, seconds
    :param func: function reference without arguments
    :param trigger: str|apscheduler.triggers.base.BaseTrigger trigger: trigger that determines when
            ``func`` is called
    """
    from flask_monitoringdashboard.core import custom_graph

    graph_id = custom_graph.register_graph(title)
    custom_graph.add_background_job(func, graph_id, trigger, **schedule)


def add_database_pruning_schedule(weeks_to_keep, delete_custom_graph_data, **schedule):
    """
    Add a scheduled job to prune the database of Request and optionally CustomGraph data older than the specified

    :param weeks_to_keep: number of weeks to keep in the database
    :param delete_custom_graph_data: flag telling if CustomGraph data should be deleted as well
    :param schedule: dict containing cron schedule values
    """
    from flask_monitoringdashboard.core import database_pruning

    database_pruning.add_background_pruning_job(weeks_to_keep, delete_custom_graph_data, **schedule)
