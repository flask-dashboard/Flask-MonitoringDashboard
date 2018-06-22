"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""
import random

from flask import Flask


def create_app():
    import flask_monitoringdashboard as dashboard
    import time

    app = Flask(__name__)

    dashboard.config.version = '3.1'
    dashboard.bind(app)

    def f():
        time.sleep(2)
        time.sleep(1)

    @app.route('/endpoint')
    def endpoint():
        f()
        return 'Ok'

    return app


if __name__ == '__main__':
    create_app().run(debug=True, threaded=True)
