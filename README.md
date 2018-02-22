# Automatic monitoring dashboard
Dashboard for automatic monitoring of python web services

This is a flask extension that can be added to your existing flask application.

It measures which python functions are heavily used and which are not. 

You can see the execution time and last access time per endpoint.

Also, unit tests can be run by TravisCI and monitored.

### Status
[![Build Status](https://travis-ci.org/flask-dashboard/Flask-Monitoring-Dashboard.svg?branch=master)](https://travis-ci.org/flask-dashboard/Flask-Monitoring-Dashboard.svg?branch=master)

### Testing
If you want to run the unit test locally, use the following command
```
    python setup.py test
```

## Installation
To install from source, download the source code, then run this:

    python setup.py install

Or install with pip:
    
    pip install flask_monitoring_dashboard
    
### Setup
Adding the extension to your flask app is simple:

    from flask import Flask
    import dashboard

    user_app = Flask(__name__)
    dashboard.config.init_from(file='/<path to your config file>/config.cfg')

    def get_session_id():
        # Implement your own function for obtaining the user variable here.
        return "12345"

    dashboard.config.get_group_by = get_session_id
    dashboard.bind(app=user_app)
    
Instead of having a hardcoded string containing the location of the config file in the code above, it is also possible 
to define an environment variable that specifies the location of this config file.
The line should then be `dashboard.config.init_from(envvar='DASHBOARD_CONFIG')`. This will configure the dashboard based on the file 
provided in the environment variable called `DASHBOARD_CONFIG`.
    
## Usage
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

## TravisCI unit testing
To enable Travis to run your unit tests and send the results to the dashboard, four steps have to be taken:

1. Update the config file ('config.cfg') to include three additional values, TEST_DIR, SUBMIT_RESULTS_URL and N.
    - TEST_DIR specifies where the unit tests reside.
    - SUBMIT_RESULTS_URL specifies where Travis should upload the test results to. When left out, the results will not
    be sent anywhere, but the performance collection process will still run.
    - N specifies the number of times Travis should run each unit test. 

2. The installation requirement for the dashboard has to be added to the 'setup.py' file of your app:

    dependency_links=["https://github.com/flask-dashboard/Flask-Monitoring-Dashboard/tarball/master#egg=flask_monitoring_dashboard"]
    
    install_requires=('flask_monitoring_dashboard')

3. In your '.travis.yml' file, three script commands should be added:

    script:
      - export DASHBOARD_CONFIG=./config.cfg
      - export DASHBOARD_LOG_DIR=./logs/
      - python -m dashboard.collect_performance

   The config environment variable specifies where the performance collection process can find the config file.
The log directory environment variable specifies where the performance collection process should place the logs it uses.
The third command will start the actual performance collection process.

4. A method that is executed after every request should be added to the blueprint of your app. 
This is done by the dashboard automatically when the blueprint is passed to the binding function like so: `dashboard.bind(app=app, blue_print=api)`.
This extra method is needed for the logging, and without it, the unit test results cannot be grouped by endpoint that they test.

## Screenshots
![Screenshot 1](/docs/img/screenshot1.png)
![Screenshot 2](/docs/img/screenshot2.png)
