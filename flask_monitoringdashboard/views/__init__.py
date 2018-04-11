"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from flask_monitoringdashboard import blueprint, loc
from flask.helpers import send_from_directory
from flask import redirect, url_for

# Import more route-functions
from . import auth
from . import dashboard
from . import rules
from . import settings
from . import testmonitor
from . import result
from . import export_data


@blueprint.route('/static/<path:filename>')
def static(filename):
    """
    Serve static files
    :param filename: filename in the /static file
    :return: content of the file
    """
    return send_from_directory(loc() + 'static', filename)


@blueprint.route('/')
def index():
    """
    Redirect to the default page
    """
    return redirect(url_for('dashboard.overview'))
