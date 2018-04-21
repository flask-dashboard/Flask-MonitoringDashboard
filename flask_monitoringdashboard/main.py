"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask, redirect, url_for


def create_app():
    import flask_monitoringdashboard as dashboard

    app = Flask(__name__)

    dashboard.config.outlier_detection_constant = 99
    dashboard.config.group_by = 'User', lambda: 3

    dashboard.bind(app=app)

    @app.route('/')
    def main():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint')
    def endpoint():
        return redirect(url_for('dashboard.index'))

    return app


if __name__ == '__main__':
    from flask_monitoringdashboard.database.function_calls import get_median
    import datetime
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    print(get_median('main', today))
    create_app().run(debug=True)
