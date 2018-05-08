# Flask Monitoring Dashboard
[![Build Status](https://travis-ci.org/flask-dashboard/Flask-MonitoringDashboard.svg?branch=master)](https://travis-ci.org/flask-dashboard/Flask-MonitoringDashboard)
[![Documentation Status](https://readthedocs.org/projects/flask-monitoringdashboard/badge/?version=latest)](http://flask-monitoringdashboard.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard/branch/master/graph/badge.svg)](https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard)
[![PyPI version](https://badge.fury.io/py/Flask-MonitoringDashboard.svg)](https://badge.fury.io/py/Flask-MonitoringDashboard)
[![Gitter chat](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Flask-MonitoringDashboard/Lobby)
[![Py-version](https://img.shields.io/pypi/pyversions/flask_monitoringdashboard.svg)](https://img.shields.io/pypi/pyversions/flask_monitoringdashboard.svg)
[![Downloads](http://pepy.tech/badge/flask-monitoringdashboard)](http://pepy.tech/count/flask-monitoringdashboard)

Dashboard for automatic monitoring of Flask web-services.

The Flask Monitoring Dashboard is an extension that offers four main functionalities with little effort from the Flask developer:
- **Monitor the Flask application:**
Our Dashboard allows you to see which endpoints process a lot of request and how fast. 
Additionally, it provides information about the evolving performance of an endpoint throughout different versions if you’re using git.
- **Monitor your test coverage:**
The dashboard allows you to find out which endpoints are covered by unit tests, allowing also for integration with Travis for automation purposes. 
For more information, see [this file](http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html#test-coverage-monitoring).
- **Collect extra information about outliers:**
Outliers are requests that take much longer to process than regular requests. 
The dashboard automatically detects that a request is an outlier and stores extra information about it (stack trace, request values, Request headers, Request environment).
- **Visualize the collected data in a number useful graphs:**
The dashboard is automatically added to your existing Flask application.
You can view the results by default using the default endpoint (this can be configured to another route):

    [/dashboard](http://localhost:5000/dashboard)

For a more advanced documentation, take a look at the information on [this site](http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html).

## Installation
To install from source, download the source code, then run this:

    python setup.py install

Or install with pip:
    
    pip install flask_monitoringdashboard
    
### Setup
Adding the extension to your Flask app is simple:

    from flask import Flask
    import flask_monitoringdashboard as dashboard

    app = Flask(__name__)
    dashboard.bind(app)
 
## Documentation
For a more advanced documentation, see [this site](http://flask-monitoringdashboard.readthedocs.io).

## Screenshots
![Screenshot 1](/docs/img/screenshot1.png)
![Screenshot 2](/docs/img/screenshot2.png)
