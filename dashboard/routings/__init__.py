"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from dashboard import blueprint, loc, user_app
from flask.helpers import send_from_directory
from flask import redirect, url_for

# Import more route-functions
import dashboard.routings.login
import dashboard.routings.setup
import dashboard.routings.result
import dashboard.routings.export_data
import dashboard.routings.measurements

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
