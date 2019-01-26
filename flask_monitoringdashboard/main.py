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

    dashboard.config.version = '3.0'
    dashboard.config.database_name = 'mysql+pymysql://root:pass@localhost:3306/zeeguu'
    dashboard.config.group_by = '2'
    dashboard.config.outlier_detection_constant = 0
    dashboard.bind(app)

    def f():
        time.sleep(2)
        time.sleep(1)

    @app.route('/endpoint')
    def endpoint():
        f()
        return 'Ok'

    @app.route('/endpoint2')
    def endpoint2():
        time.sleep(0.1)
        return 'Ok'

    @app.route('/endpoint3')
    def endpoint3():
        if random.randint(0, 1) == 0:
            time.sleep(0.1)
        else:
            time.sleep(0.2)
        return 'Ok'
    return app


if __name__ == '__main__':
    create_app().run()
