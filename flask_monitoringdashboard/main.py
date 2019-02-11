"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""
import random
import time

from flask import Flask

import flask_monitoringdashboard as dashboard

app = Flask(__name__)

dashboard.config.version = '3.1'
dashboard.config.group_by = '2'
dashboard.config.database_name = 'sqlite:///data.db'
dashboard.bind(app)


def f():
    time.sleep(2)
    time.sleep(1)


@app.route('/endpoint')
def endpoint():
    f()
    return 'Ok'


@app.route('/endpoint2')
def endpoint2():
    time.sleep(0.1)
    return 'Ok'


@app.route('/endpoint3')
def endpoint3():
    if random.randint(0, 1) == 0:
        time.sleep(0.1)
    else:
        time.sleep(0.2)
    return 'Ok'


dashboard.add_graph('Graph1', 'daily', lambda: 42)
