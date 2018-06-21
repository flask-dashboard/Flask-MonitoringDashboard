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
    # dashboard.config.database_name = 'sqlite:///flask_monitoring_dashboard_v10.db'
    dashboard.config.version = '3.1'
    dashboard.bind(app)

    def f():
        time.sleep(2)
        time.sleep(1)

    @app.route('/endpoint')
    def endpoint():
        f()
        return 'Ok'

    @app.route('/endpoint1')
    def endpoint1():
        f()
        return 'Ok'

    @app.route('/endpoint2')
    def endpoint2():
        f()
        return 'Ok'

    @app.route('/endpoint3')
    def endpoint3():
        f()
        return 'Ok'

    @app.route('/endpoint4')
    def endpoint4():
        f()
        return 'Ok'

    @app.route('/endpoint5')
    def endpoint5():
        f()
        return 'Ok'

    @app.route('/endpoint6')
    def endpoint6():
        f()
        return 'Ok'

    @app.route('/endpoint7')
    def endpoint7():
        f()
        return 'Ok'

    @app.route('/endpoint8')
    def endpoint8():
        f()
        return 'Ok'

    @app.route('/endpoint9')
    def endpoint9():
        f()
        return 'Ok'

    @app.route('/endpoint10')
    def endpoint10():
        f()
        return 'Ok'

    return app


if __name__ == '__main__':
    create_app().run(debug=True, threaded=True)
