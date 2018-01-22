# Automatic monitoring dashboard
Dashboard for automatic monitoring of python web services

This is a flask extension that can be added to your existing flask application.

It measures which python functions are heavily used and which are not. 

You can see the execution time and last access time per endpoint.

Also, unit tests can be run by TravisCI and monitored.

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
    
Instead of having a hardcoded string containing the location of the config file in the code above, it is also possible to define an environment variable that specifies the location of this config file.
The line should then be `dashboard.config.from_file(None)`. This will configure the dashboard based on the file provided in the environment variable `DASHBOARD_CONFIG`.
When both a hardcoded location string and the environment variable are provided, the latter will override the former.
    
Usage
=====
Once the setup is done, a config file ('config.cfg') should be set next to the python file that contains the entry point of the app.
The following things can be configured:

    [dashboard]
    APP_VERSION=1.0
    CUSTOM_LINK=dashboard
    USERNAME=admin
    PASSWORD=admin
    GUEST_USERNAME=guest
    GUEST_PASSWORD=['dashboardguest!', 'second_pw!']
    DATABASE=sqlite:////<path to your project>/dashboard.db
    GIT=/<path to your project>/.git/
    TEST_DIR=/<path to your project>/tests/
    N=5
    SUBMIT_RESULTS_URL=http://0.0.0.0:5000/dashboard/submit-test-results
    OUTLIER_DETECTION_CONSTANT=2.5
    COLORS={'main':[0,97,255], 'static':[255,153,0]}

For more information, please refer to [this file](dashboard/config.py)

When running your app, the dashboard van be viewed by default in the route:

    /dashboard

TravisCI unit testing
=====================
To enable Travis to run your unit tests and send the results to the dashboard, four steps have to be taken.

First off, your config file for the dashboard ('config.cfg') should be updated to include three additional values, TEST_DIR, SUBMIT_RESULTS_URL and N.
The first specifies where your unit tests reside, the second where Travis should upload the test results to, and the last specifies the number of times Travis should run each unit test.
If the url for submitting test results is not specified, the results will not be sent anywhere, but the performance collection process will still run.
See the sample config file in the section above for an example.

Secondly, the installation requirement for the dashboard has to be added to the 'setup.py' file of your app:

    dependency_links=["https://github.com/flask-dashboard/Flask-Monitoring-Dashboard/tarball/master#egg=flask_monitoring_dashboard"]
    install_requires=('flask_monitoring_dashboard')

Then, in your '.travis.yml' file, three script commands should be added:

    script:
      - export DASHBOARD_CONFIG=/home/travis/build/<name>/<project>/config.cfg
      - export DASHBOARD_LOG_DIR=/home/travis/build/<name>/<project>/
      - python -m dashboard.collect_performance

Where 'name' is the name under which your project will be built by Travis, and 'project' is the name of your repository.
The config environment variable specifies where the performance collection process can find the config file.
The log directory environment variable specifies where the performance collection process should place the logs it uses.
The third command will start the actual performance collection process.

Lastly, a method that is executed after every request should be added to the blueprint of your app.
This is needed for the logging, and without it, the unit test results cannot be grouped by endpoint that they test.
The code for adding this functionality is:

```python
    import os
    import datetime
    from flask import request
    log_dir = os.getenv('DASHBOARD_LOG_DIR')
    @api.after_request
    def after_request(response):
        t1 = str(datetime.datetime.now())
        log = open(log_dir + "endpoint_hits.log", "a")
        log.write("\"{}\",\"{}\"\n".format(t1, request.endpoint))
        log.close()
        return response
```

Where 'api' is the blueprint of the app you want to run the collection of unit test performance on.

Screenshots
===========
![Screenshot 1](/images/screenshot1.png)
![Screenshot 2](/images/screenshot2.png)
