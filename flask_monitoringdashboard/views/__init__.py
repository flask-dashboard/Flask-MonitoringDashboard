"""
    Main class for adding all route-functions to user_app.
    Setup requires only to import this file. All other imports are done in this file
"""
from flask import render_template
from flask.helpers import send_from_directory

from flask_monitoringdashboard import loc, blueprint, config, static_path_exists
from flask_monitoringdashboard.core.auth import secure


@blueprint.route('/static/<path:filename>')
def static(filename):
    """
    Serve static files
    :param filename: filename in the /static file
    :return: content of the file
    """
    #return send_from_directory(loc() + 'static', filename)
    return send_from_directory(loc() + 'templates', filename)


@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')  # Catch-All URL: http://flask.pocoo.org/snippets/57/
@secure
def index(path):
    if static_path_exists(path) and path != '':
        return send_from_directory(loc() + 'templates/browser', path)
    else: 
        return send_from_directory(loc() + 'templates/browser', "index.html")
    #return render_template('index.html', 
    #    blueprint_name=config.blueprint_name, 
    #    brand_name=config.brand_name, 
    #    title_name=config.title_name,
    #    description=config.description,
    #)
