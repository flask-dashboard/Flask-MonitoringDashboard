"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask, redirect, url_for


def create_app():
    import flask_monitoringdashboard as dashboard

    app = Flask(__name__)

    dashboard.config.outlier_detection_constant = 0
    dashboard.config.group_by = 'User', 2
    dashboard.config.version = 1.0
    dashboard.config.database_name = 'sqlite:///flask_monitoringdashboard6.db'
    dashboard.bind(app)

    @app.route('/endpoint1')
    def endpoint1():
        import time
        time.sleep(2)

    @app.route('/')
    def main():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint2')
    def endpoint2():
        return redirect(url_for('dashboard.index'))

    @app.route('/outl')
    def outl():
        return 'sfsef'

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
