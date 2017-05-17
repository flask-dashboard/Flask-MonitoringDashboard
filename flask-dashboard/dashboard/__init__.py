"""
    For tracking the performances, the app should be configured using the 
    following lines of code:
        import dashboard
        from flask import Flask
        ...
        app = Flask(__name__)
        ...
        dashboard.config(app)

    The dashboard with the results that are collected can be found at:
        localhost:5000/dashboard
"""

import os
import sys
from jinja2 import Environment, FileSystemLoader

user_app = None
version = '1.0'
user_var = None
link = 'dashboard'
database_name = 'flask_database.db'
group = None


def config(app, custom_link='dashboard', app_version='1.0', git_path=None,
           db_name='flask_database.db', group_by=None):
    """
    Binding the app to this object should happen before importing the routing-
    methods below. Thus, the importing statement is part of this function.
    
    :param git_path: If you're using git, then it is easier to set the location to the .git-folder, 
    The location is relative to the file that is being used to execute the program: (sys.argv[0])
    :param group_by: applies as a filter to sort the results based on this group_by-tag.
    :param db_name: Suppose you have multiple projects where you're working on and want to 
    separate the results. Then you can specify different database_names, such that the result 
    of each project is stored in its own database.
    :param app_version: the version of the app that you use. Updating the version helps in 
    showing differences in execution times of a function over a period of time
    :param custom_link: The dashboard can be visited at localhost:5000/{{custom_link}}
    :param app: the app for which the performance has to be tracked    
    """
    assert app is not None
    global user_app, link, version, database_name, group
    user_app = app
    version = app_version
    link = custom_link
    database_name = db_name
    group = group_by

    if git_path:
        try:
            # location to git-folder
            git = str(sys.argv[0].rsplit('/', 1)[0]) + git_path
            # current hash can be found in the link in HEAD-file in git-folder
            # The file is specified by: 'ref: <location>'
            git_file = (open(os.path.join(git, 'HEAD')).read().rsplit(': ', 1)[1]).rstrip()
            # read the git-version
            version = open(git + '/' + git_file).read()
        except IOError:
            print("Error reading one of the files to retrieve the current git-version.")
            raise

    # Add wrappers to the endpoints that have to be monitored
    from dashboard.measurement import init_measurement
    user_app.before_first_request(init_measurement)
    import dashboard.routings


# get current location of the project
def loc():
    s = os.path.abspath(os.path.dirname(__file__))
    return str(s.rsplit('/', 1)[0]) + '/'

# environment is used for serving templates from the right-folder
env = Environment(loader=FileSystemLoader(loc() + 'templates'))
