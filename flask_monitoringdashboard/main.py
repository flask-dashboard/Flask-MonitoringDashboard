"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask


def create_app():
    import flask_monitoringdashboard as dashboard
    import time

    app = Flask(__name__)

    dashboard.config.version = '3.1'
    dashboard.config.database_name = 'sqlite:///flask_monitoring_dashboard_v10.db'
    # dashboard.config.database_name = 'postgresql://user:password@localhost:5432/db_name'
    # dashboard.config.database_name = 'mysql+pymysql://user:password@localhost:3306/db_name'
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
