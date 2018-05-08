"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""

from flask import Flask, redirect, url_for


def create_app():
    import flask_monitoringdashboard as dashboard

    app = Flask(__name__)

    dashboard.config.outlier_detection_constant = 0
    dashboard.config.group_by = 'User', 1
    dashboard.config.version = 1.0
    dashboard.config.database_name = 'mysql+pymysql://root@localhost/flask_test'
    dashboard.bind(app)

    @app.route('/endpoint1')
    def endpoint1():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint2')
    def endpoint2():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint3')
    def endpoint3():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint4')
    def endpoint4():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint5')
    def endpoint5():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint6')
    def endpoint6():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint7')
    def endpoint7():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint8')
    def endpoint8():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint9')
    def endpoint9():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint10')
    def endpoint10():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint11')
    def endpoint11():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint12')
    def endpoint12():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint13')
    def endpoint13():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint14')
    def endpoint14():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint15')
    def endpoint15():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint16')
    def endpoint16():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint17')
    def endpoint17():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint18')
    def endpoint18():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint19')
    def endpoint19():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint20')
    def endpoint20():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint21')
    def endpoint21():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint22')
    def endpoint22():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint23')
    def endpoint23():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint24')
    def endpoint24():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint25')
    def endpoint25():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint26')
    def endpoint26():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint27')
    def endpoint27():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint28')
    def endpoint28():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint29')
    def endpoint29():
        return redirect(url_for('dashboard.index'))

    @app.route('/endpoint30')
    def endpoint30():
        return redirect(url_for('dashboard.index'))

    @app.route('/')
    def main():
        return redirect(url_for('dashboard.index'))

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
