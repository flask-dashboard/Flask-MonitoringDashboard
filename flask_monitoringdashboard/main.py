"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask, redirect, url_for
from pytz import timezone


def create_app():
    import flask_monitoringdashboard as dashboard

    app = Flask(__name__)

    dashboard.config.outlier_detection_constant = 0
    dashboard.config.group_by = 'User', 2
    dashboard.config.version = 2.0
    dashboard.config.database_name = 'sqlite:///flask_monitoringdashboard.db'
    dashboard.config.timezone = timezone('Pacific/Kiritimati')
    dashboard.bind(app)

    @app.route('/endpoint1')
    def endpoint1():
        import time
        time.sleep(2)
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint2')
    def endpoint2():
        return redirect(url_for('dashboard.index'))

    @app.route('/outl')
    def outl():
        return 'sfsef'

    @app.route('/')
    def main():
        import time
        time.sleep(2)
        return redirect(url_for('dashboard.index'))

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
