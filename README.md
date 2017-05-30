# flask-dashboard
Dashboard for automatic monitoring of python web services

This is a flask extension that can be added to your existing flask application.

It measures which python functions are heavily used and which are not. Moreover, you can see the execution time per endpoint.

Installation
============
To install from source, download the source code, then run this:

    python setup.py install
    
Setup
=====
Adding the extension to your flask app is simple:

    from flask import Flask
    import dashboard

    app = Flask(__name__)
    dashboard.bind(app)
    
Usage
=====
Once the setup is done, a config file should be set next to the python file that contains the entry point of the app.
The following things should be set for best performance:

    [dashboard]
    DATABASE=sqlite:////<path to your project>/flask-dashboard.db
    GIT=/<path to your project>/flask-dashboard/.git/
    TEST_DIR=/<path to your project>/flask-dashboard/tests/

When running your app, the dashboard van be viewed by default in the route:

    /dashboard
