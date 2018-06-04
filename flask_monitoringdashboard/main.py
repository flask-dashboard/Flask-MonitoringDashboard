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

    dashboard.config.outlier_detection_constant = 0
    dashboard.config.database_name = 'sqlite:///flask_monitoringdashboard_v7.db'
    dashboard.bind(app)

    def f():
        time.sleep(1)

    def g():
        f()

    @app.route('/endpoint')
    def endpoint():
        if random.randint(0, 1) == 0:
            f()
        else:
            g()

        i = 0
        while i < 500:
            time.sleep(0.001)
            i += 1

        if random.randint(0, 1) == 0:
            f()
        else:
            g()

        return 'Ok'

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
