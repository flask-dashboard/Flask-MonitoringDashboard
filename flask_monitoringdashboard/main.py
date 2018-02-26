"""
    This file can be executed for developing purposes. It is not used, when the flask_monitoring_dashboard is
    attached to an existing flask application.
"""

from flask import Flask, redirect, url_for
import flask_monitoringdashboard
import os

user_app = Flask(__name__)
here = os.path.abspath(os.path.dirname(__file__))
flask_monitoringdashboard.config.init_from(file=here + '/config.cfg')


def get_session_id():
    # implement here your own custom function
    return '12345'


flask_monitoringdashboard.config.get_group_by = get_session_id
flask_monitoringdashboard.bind(app=user_app)


@user_app.route('/')
def main():
    return redirect(url_for('flask_monitoringdashboard.index'))


if __name__ == '__main__':
    user_app.run(debug=True, host='0.0.0.0')
