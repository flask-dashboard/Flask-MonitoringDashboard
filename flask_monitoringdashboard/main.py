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
    dashboard.config.version = 1.5
    dashboard.config.database_name = 'sqlite:///flask_monitoringdashboard.db'
    dashboard.bind(app)

    def f():
        import time
        time.sleep(1)

    def g():
        f()

    def h():
        g()

    @app.route('/endpoint')
    def endpoint():
        import time
        time.sleep(1)
        f()
        g()
        h()
        return ''

    @app.route('/')
    def main():
        return redirect(url_for('dashboard.index'))

    return app


if __name__ == '__main__':
    app = create_app().run(debug=True)
