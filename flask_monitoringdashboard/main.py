"""
    This file can be executed for developing purposes.
    To run use

        python main.py

    Note: This is not used when the flask_monitoring_dashboard
    is attached to your flask application.
"""
from random import random
import datetime
import time

from flask import Flask

import flask_monitoringdashboard as dashboard

app = Flask(__name__)

dashboard.config.version = '3.2'
dashboard.config.group_by = '2'
dashboard.config.database_name = 'mysql://root:password@127.0.0.1/fmd'


# dashboard.config.database_name = 'mysql+pymysql://user:password@localhost:3306/db1'
# dashboard.config.database_name = 'postgresql://user:password@localhost:5432/mydb'


def on_the_minute():
    print(f"On the minute: {datetime.datetime.now()}")
    return int(random() * 100 // 10)


minute_schedule = {'second': 00}

dashboard.add_graph("On Half Minute", on_the_minute, "cron", **minute_schedule)


def every_ten_seconds():
    print(f"every_ten_seconds!!! {datetime.datetime.now()}")
    return int(random() * 100 // 10)


every_ten_seconds_schedule = {'seconds': 10}

dashboard.add_graph("Every 10 Seconds", every_ten_seconds, "interval", **every_ten_seconds_schedule)

dashboard.bind(app)


@app.route('/endpoint')
def endpoint():

    print("Hello, world")
    return 'Ok'


@app.route('/endpoint2')
def endpoint2():
    time.sleep(0.5)
    return 'Ok', 400


@app.route('/endpoint3')
def endpoint3():
    if random.randint(0, 1) == 0:
        time.sleep(0.1)
    else:
        time.sleep(0.2)
    return 'Ok'


@app.route('/endpoint4')
def endpoint4():
    time.sleep(0.5)
    return 'Ok'


@app.route('/endpoint5')
def endpoint5():
    time.sleep(0.2)
    return 'Ok'


def my_func():
    # here should be something actually useful
    return 33.3


app.run()
