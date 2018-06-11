"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask


def create_app():
    import flask_monitoringdashboard as dashboard
    import time

    app = Flask(__name__)

    dashboard.config.outlier_detection_constant = 0
    dashboard.config.database_name = 'sqlite:///flask_monitoring_dashboard_v10.db'
    dashboard.bind(app)

    def f(duration=1):
        time.sleep(duration)

    def g():
        f()

    @app.route('/endpoint')
    def endpoint():
        if random.randint(0, 1) == 0:
            g()
        else:
            f()
        return 'Ok'

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
