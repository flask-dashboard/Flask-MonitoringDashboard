<h1 align="center">
    <img src="/docs/img/header.png" width="600">
    <br>
    Flask Monitoring Dashboard
    <br>
</h1>

<p align="center">
A dashboard for automatic monitoring of <a href="https://flask.palletsprojects.com/" target="_blank">Flask</a> web-services.
</p>

<span align="center">
    
![Build Status](https://github.com/flask-dashboard/Flask-MonitoringDashboard/workflows/Python%20Testing/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/flask-monitoringdashboard/badge/?version=latest)](http://flask-monitoringdashboard.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard/branch/master/graph/badge.svg)](https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard)
[![PyPI version](https://badge.fury.io/py/Flask-MonitoringDashboard.svg)](https://badge.fury.io/py/Flask-MonitoringDashboard)
[![Py-version](https://img.shields.io/pypi/pyversions/flask_monitoringdashboard.svg)](https://img.shields.io/pypi/pyversions/flask_monitoringdashboard.svg)
[![Downloads](http://pepy.tech/badge/flask-monitoringdashboard)](http://pepy.tech/count/flask-monitoringdashboard)
[![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Monitor%20your%20Flask%20application%20with%20the%20Flask%20Monitoring%20Dashboard&url=https://github.com/flask-dashboard/Flask-MonitoringDashboard&hashtags=fmd,flask,python)

</span>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How to use</a> •
  <a href="#live-demo">Live Demo</a> •
  <a href="#feedback">Feedback</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#license">License</a>
</p>

![gif](/docs/img/fmd_video.gif)

## Motivation

<img width="592" alt="image" src="https://user-images.githubusercontent.com/464519/210054732-bf97cfaa-fb66-4a9f-affb-7004f531b34c.png">


## Key Features
The Flask Monitoring Dashboard is an extension for Flask applications that offers four main functionalities with little effort from the Flask developer:

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


## How to use

#### Installation
To install from source, download the source code, then run this:

    python setup.py install

Or install with pip:
    
    pip install flask_monitoringdashboard
    
#### Setup
Adding the extension to your Flask app is simple:

    from flask import Flask
    import flask_monitoringdashboard as dashboard

    app = Flask(__name__)
    
    @app.route("/test")
    def test():
	    return 'ok'
    
    dashboard.bind(app)
    app.run()

## Live Demo
To view a live deployment of the Flask-MonitoringDashboard, check [this site](https://fmd-master.herokuapp.com/).
Use the credentials u:`admin`, p:`admin` to log in.

## Feedback
In order to improve our Flask-MonitoringDashboard, we would like to hear from you! Therefore, we made a questionnaire
with a few questions. Filling in this form takes less than 3 minutes. You can find the form [here](https://goo.gl/forms/IqRrjGDDXe44q5ZV2).

Alternatively, feel free to write to [our email-address](mailto:flask.monitoringdashboard@gmail.com).
 
## Documentation
For more advanced documentation, see [this site](http://flask-monitoringdashboard.readthedocs.io).
If you run into trouble migrating from version 1.X.X to version 2.0.0, this site will help you solve this too.

## Screenshots
![Screenshot 1](/docs/img/ss1.png)
![Screenshot 2](/docs/img/ss2.png)
![Screenshot 3](/docs/img/ss3.png)
![Screenshot 4](/docs/img/ss4.png)
![Screenshot 5](/docs/img/ss5.png)

## Development
If you like our project, and willing to contribute, you can get started by cloning it and then running the following command:

    . ./config/install.sh

For more information, check [this page](https://flask-monitoringdashboard.readthedocs.io/en/latest/developing.html).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
