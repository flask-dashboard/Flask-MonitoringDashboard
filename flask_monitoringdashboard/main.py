"""This file can be executed for developing purposes.
To run use:

>>> python main.py

Note: This is not used when the flask_monitoring_dashboard
is attached to your flask application.
"""

import time
import json
from random import random, randint

from flask import Flask, redirect, url_for

import flask_monitoringdashboard as dashboard

app = Flask(__name__)
dashboard.config.init_from(file='config.cfg')

dashboard.config.version = "3.2"
dashboard.config.group_by = "2"
dashboard.config.database_name = "sqlite:///data.db"
# dashboard.config.database_name = 'mysql+pymysql://user:password@localhost:3306/db1'
# dashboard.config.database_name = 'postgresql://user:password@localhost:5432/mydb'


def on_the_minute():
    return int(random() * 100 // 10)


minute_schedule = {"second": 00}
dashboard.add_graph("On Half Minute", on_the_minute, "cron", **minute_schedule)


def every_ten_seconds():
    return int(random() * 100 // 10)


every_ten_seconds_schedule = {"seconds": 10}
dashboard.add_graph(
    "Every 10 Seconds", every_ten_seconds, "interval", **every_ten_seconds_schedule
)


@app.route("/")
def to_dashboard():
    return redirect(url_for(dashboard.config.blueprint_name + ".login"))


@app.route("/endpoint")
def endpoint():
    # if session_scope is imported at the top of the file, the database config won't take effect
    from flask_monitoringdashboard.database import session_scope

    with session_scope() as session:
        print(session.bind.dialect.name)

    print("Hello, world")
    return "Ok"


@app.route("/endpoint2")
def endpoint2():
    time.sleep(0.5)
    return "Ok", 400


@app.route("/endpoint3")
def endpoint3():
    if randint(0, 1) == 0:
        time.sleep(0.1)
    else:
        time.sleep(0.2)
    return "Ok"


@app.route("/endpoint4")
def endpoint4():
    time.sleep(0.5)
    return "Ok"


@app.route("/endpoint5")
def endpoint5():
    time.sleep(0.2)
    return "Ok"


def reraised_and_captured_exception():
    try:
        raise Exception("åhhh nej")
    except BaseException as e:
        dashboard.capture(e)
        try:
            e.args = (f"Reraised exception: {e.args[0]}",)
            raise e
        except BaseException as e2:
            dashboard.capture(e2)
            e.args = (f"Rereraised exception: {e.args[0]} (uncaught)",)
            raise e2


def non_app_exception():
    json.loads('{"invalid_json": }')


def recursive_function(n):
    if n == 0:
        raise Exception("recursive åhhh nej")
    elif n % 3 == 0:
        return recursive_function(n - 2)
    elif n % 3 == 1:
        return recursive_function(n - 1)
    else:
        return recursive_function(n - 1)


def b():
    n = randint(1, 3)
    if n == 1:
        return reraised_and_captured_exception()
    if n == 2:
        return non_app_exception()
    if n == 3:
        return recursive_function(100)


def c():
    return b()


def d():
    return c


@app.route("/throws")
def throws():
    time.sleep(0.2)
    d()()
    return "Ok"

@app.route("/throws_direct")
def throws_direct():
    time.sleep(0.2)
    raise Exception("This is an uncaught exception!")

@app.route("/throws_di")
def throws_di():
    time.sleep(0.2)
    raise ArithmeticError("This is an uncaught exception!")

@app.route("/throws_n")
def throws_f():
    time.sleep(0.2)
    raise ArithmeticError("This is an uncaught exception!")

def my_func():
    # here should be something actually useful
    return 33.3

if __name__ == "__main__":
    dashboard.bind(app)
    app.run(port=4200)
