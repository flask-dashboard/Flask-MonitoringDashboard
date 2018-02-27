"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from flask_monitoringdashboard import blueprint, loc, user_app
from flask.helpers import send_from_directory
from flask import redirect, url_for

# Import more route-functions
import flask_monitoringdashboard.routings.login
import flask_monitoringdashboard.routings.setup
import flask_monitoringdashboard.routings.result
import flask_monitoringdashboard.routings.export_data
import flask_monitoringdashboard.routings.measurements

# Provide a secret-key for using WTF-forms
if user_app.secret_key is None:
    user_app.secret_key = 'my-secret-key'


# Rule for serving static files
@blueprint.route('/static/<path:filename>')
def static(filename):
    return send_from_directory(loc() + 'static', filename)


# All rules below are for viewing the dashboard-pages
@blueprint.route('/')
def index():
    return redirect(url_for('dashboard.overview'))
