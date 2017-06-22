# Automatic monitoring dashboard
Dashboard for automatic monitoring of python web services

This is a flask extension that can be added to your existing flask application.

It measures which python functions are heavily used and which are not. 
You can see the execution time and last access time per endpoint.
Also, unit tests can be run and monitored.

Installation
============
To install from source, download the source code, then run this:

    python setup.py install

Or install with pip:
    
    pip install flask_monitoring_dashboard
    
Setup
=====
Adding the extension to your flask app is simple:

    from flask import Flask
    import dashboard

    user_app = Flask(__name__)
    dashboard.config.from_file('/<path to your config file>/config.cfg')

    def get_session_id():
        # Implement your own function for obtaining the user variable here.
        return "12345"

    dashboard.config.get_group_by = get_session_id
    dashboard.bind(app=user_app)
    
Usage
=====
Once the setup is done, a config file ('config.cfg') should be set next to the python file that contains the entry point of the app.
The following things can be configured:

    [dashboard]
    APP_VERSION=1.0
    CUSTOM_LINK=dashboard
    USERNAME=admin
    PASSWORD=admin
    DATABASE=sqlite:////<path to your project>/dashboard.db
    GIT=/<path to your project>/dashboard/.git/
    TEST_DIR=/<path to your project>/dashboard/tests/
    OUTLIER_DETECTION_CONSTANT=2.5

For more information: [see this file](dashboard/config.py)

When running your app, the dashboard van be viewed by default in the route:

    /dashboard
