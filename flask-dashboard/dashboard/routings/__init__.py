"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from dashboard import user_app, loc, env, link
from dashboard.security import secure
from flask.helpers import send_from_directory
from flask import session

# Import more route-functions
import dashboard.routings.login
import dashboard.routings.setup
import dashboard.routings.result

# Provide a secret-key for using WTF-forms
if user_app.secret_key is None:
    user_app.secret_key = 'my-secret-key'

user_app.jinja_env.add_extension('jinja2.ext.loopcontrols')


# Rule for serving static files
@user_app.route('/static-' + link + '/<path:file>')
def serve_static_file(file):
    return send_from_directory(loc() + 'static', file)


# All rules below are for viewing the dashboard-pages
@user_app.route('/' + link)
@secure
def dashboard_index():
    return env.get_template('index.html').render(link=link, session=session)


@user_app.route('/' + link + '/how-to-install')
@secure
def dashboard_how_to_install():
    return env.get_template('how-to-install.html').render(link=link, session=session)


@user_app.route('/' + link + '/how-to-use')
@secure
def dashboard_how_to_use():
    return env.get_template('how-to-use.html').render(link=link, session=session)
