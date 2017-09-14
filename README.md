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
    GUEST_PASSWORD=dashboardguest!
    DATABASE=sqlite:////<path to your project>/dashboard.db
    GIT=/<path to your project>/dashboard/.git/
    TEST_DIR=/<path to your project>/dashboard/tests/
    N=5
    SUBMIT_RESULTS_URL=http://0.0.0.0:5000/dashboard/submit-test-results
    OUTLIER_DETECTION_CONSTANT=2.5
    COLORS={'main':[0,97,255], 'static':[255,153,0]}

For more information: [see this file](dashboard/config.py)

When running your app, the dashboard van be viewed by default in the route:

    /dashboard

TravisCI unit testing
=====================
To enable Travis to run your unit tests and send the results to the dashboard, four steps have to be taken.

First off, the file 'collect_performance.py' (which comes with the dashboard) should be copied to the directory where your '.travis.yml' file resides.

Secondly, your config file for the dashboard ('config.cfg') should be updated to include three additional values, TEST_DIR, SUBMIT_RESULTS_URL and N.
The first specifies where your unit tests reside, the second where Travis should upload the test results to, and the third specifies the number of times Travis should run each unit test.
See the sample config file in the section above for more details.

Then, a dependency link to the dashboard has to be added to the 'setup.py' file of your app:

    dependency_links=["git+https://github.com/mircealungu/automatic-monitoring-dashboard.git#egg=flask_monitoring_dashboard"],
    install_requires=('flask_monitoring_dashboard')

Lastly, in your '.travis.yml' file, two script commands should be added:

    script:
      - export DASHBOARD_CONFIG=config.cfg
      - python ./collect_performance.py

Screenshots
===========
![Screenshot 1](/images/screenshot1.png)
![Screenshot 2](/images/screenshot2.png)
