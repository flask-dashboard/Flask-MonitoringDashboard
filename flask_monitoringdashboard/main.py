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
    dashboard.config.version = '3.1'
    dashboard.bind(app)

    def f(i=5):
        if i == 0:
            time.sleep(1)
        else:
            f(i-1)

    def g():
        time.sleep(1)

    @app.route('/endpoint')
    def endpoint():
        if random.randint(0, 1):
            f()
        else:
            g()
        return 'Ok'

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
