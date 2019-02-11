# Flask Monitoring Dashboard
[![Build Status](https://travis-ci.org/flask-dashboard/Flask-MonitoringDashboard.svg?branch=master)](https://travis-ci.org/flask-dashboard/Flask-MonitoringDashboard)
[![Documentation Status](https://readthedocs.org/projects/flask-monitoringdashboard/badge/?version=latest)](http://flask-monitoringdashboard.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard/branch/master/graph/badge.svg)](https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard)
[![PyPI version](https://badge.fury.io/py/Flask-MonitoringDashboard.svg)](https://badge.fury.io/py/Flask-MonitoringDashboard)
[![Py-version](https://img.shields.io/pypi/pyversions/flask_monitoringdashboard.svg)](https://img.shields.io/pypi/pyversions/flask_monitoringdashboard.svg)
[![Downloads](http://pepy.tech/badge/flask-monitoringdashboard)](http://pepy.tech/count/flask-monitoringdashboard)

Dashboard for automatic monitoring of Flask web-services.

The Flask Monitoring Dashboard is an extension that offers four main functionalities with little effort from the Flask developer:

- **Monitor the performance and utilization:**
  The Dashboard allows you to see which endpoints process a lot of requests and how fast. 
  Additionally, it provides information about the evolving performance of an endpoint throughout different versions if you're using git.

- **Profile requests and endpoints:**
  The execution path of every request is tracked and stored into the database. This allows you to gain
  insight over which functions in your code take the most time to execute. Since all requests for an 
  endpoint are also merged together, the Dashboard provides an overview of which functions are used in
  which endpoint.

- **Collect extra information about outliers:**
  Outliers are requests that take much longer to process than regular requests. 
  The Dashboard automatically detects that a request is an outlier and stores extra information about it (stack trace, request values, Request headers, Request environment).

- **Collect additional information about your Flask-application:**
  Suppose you have an User-table and you want to know how many users are registered on your Flask-application.
  Then, you can run the following query: 'SELECT Count(*) FROM USERS;'. But this is just annoying to do regularly.
  Therefore, you can configure this in the Flask-MonitoringDashboard, which will provide you this information per day (or other time interval).
  
  
The dashboard is automatically added to your existing Flask application.
You can view the results by default using the default endpoint (this can be configured to another route):

   [/dashboard](http://localhost:5000/dashboard)

For more advanced documentation, take a look at the information on [this site](http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html).

## Live demo
To view a live deployment of the Flask-MonitoringDashboard, check [this site](https://flask-monitoringdashboard.herokuapp.com/).


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
For more advanced documentation, see [this site](http://flask-monitoringdashboard.readthedocs.io).
If you run into trouble migrating from version 1.X.X to version 2.0.0, this site also helps you solve this.

## Screenshots
![Screenshot 1](/docs/img/ss1.png)
![Screenshot 2](/docs/img/ss2.png)
![Screenshot 3](/docs/img/ss3.png)
![Screenshot 4](/docs/img/ss4.png)
![Screenshot 5](/docs/img/ss5.png)
