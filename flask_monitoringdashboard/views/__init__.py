"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from flask import render_template
from flask.helpers import send_from_directory

from flask_monitoringdashboard import blueprint, loc
# Import more route-functions
from . import auth
from flask_monitoringdashboard.api import get_info
# from . import dashboard
# from . import details
# from . import export
# from . import rules
# from . import configuration
# from . import testmonitor


@blueprint.route('/static/<path:filename>')
def static(filename):
    """
    Serve static files
    :param filename: filename in the /static file
    :return: content of the file
    """
    return send_from_directory(loc() + 'static', filename)


@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
def angular(path):
    return render_template('angular.html')