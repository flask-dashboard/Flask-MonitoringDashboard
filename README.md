# Flask Monitoring Dashboard
Dashboard for automatic monitoring of Flask web services.

The Flask Monitoring Dashboard provides 4 main functionalities:
- **Monitor the Flask application:**
This Flask extensions finds all your endpoints.
You can choose which endpoints you want to monitor and which not.
Monitoring and endpoint allows you to see which endpoints are being processed quickly, and which are not.
Additionally, it provides information about the performance of the endpoint throughout different versions and different users.
- **Monitor your test coverage:**
Find out what endpoints are covered by unittest. 
For more information, see [this file](http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html#test-coverage-monitoring).
- **Collect extra information about outliers:**
Outliers are requests that take way longer to process than regular requests.
The dashboard stores more information about outliers, such as:
    - The stacktrace in which it got stuck.
    - Request values.
    - Request headers.
    - Request environment.
- **Visualize the collected data in a number useful graphs:**
The dashboard is automatically added to your existing Flask application.
When running your app, the dashboard van be viewed by default in the route:

    [/dashboard](http://localhost:5000/dashboard)

### Status
[![Build Status](https://travis-ci.org/flask-dashboard/Flask-MonitoringDashboard.svg?branch=master)](https://travis-ci.org/flask-dashboard/Flask-MonitoringDashboard.svg?branch=master)
[![Documentation Status](https://readthedocs.org/projects/flask-monitoringdashboard/badge/?version=latest)](http://flask-monitoringdashboard.readthedocs.io/en/latest/?badge=latest)

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
