"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from dashboard import blueprint, loc, config, user_app
from dashboard.security import secure
from flask.helpers import send_from_directory
from flask import session, render_template

# Import more route-functions
import dashboard.routings.login
import dashboard.routings.setup
import dashboard.routings.result

# Provide a secret-key for using WTF-forms
if user_app.secret_key is None:
    user_app.secret_key = 'my-secret-key'


# Rule for serving static files
@blueprint.route('/static/<path:filename>')
def static(filename):
    return send_from_directory(loc() + 'static', filename)


# All rules below are for viewing the dashboard-pages
@blueprint.route('/')
@secure
def index():
    return render_template('index.html', link=config.link, session=session)


@blueprint.route('/how-to-install')
@secure
def how_to_install():
    return render_template('how-to-install.html', link=config.link, session=session)


@blueprint.route('/how-to-use')
@secure
def how_to_use():
    return render_template('how-to-use.html', link=config.link, session=session)
