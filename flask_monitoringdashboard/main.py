"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask


def create_app():
    import flask_monitoringdashboard as dashboard
    import time

    app = Flask(__name__)

    dashboard.config.outlier_detection_constant = 1
    dashboard.config.database_name = 'sqlite:///flask_monitoringdashboard_v10.db'
    dashboard.config.sampling_period = .1
    dashboard.bind(app)

    def f(duration=1):
        time.sleep(duration)

    def g():
        f()

    def h():
        g()

    def i():
        h()

    @app.route('/endpoint')
    def endpoint():
        i()
        return 'Ok'

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
