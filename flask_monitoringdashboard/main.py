"""
    This file can be executed for developing purposes.
    It is not used when the flask_monitoring_dashboard is attached to an existing flask application.
"""
import random
import time

from flask import Flask


import flask_monitoringdashboard as dashboard
app = Flask(__name__)

dashboard.config.version = '3.2'
dashboard.config.group_by = '2'
dashboard.config.database_name = 'sqlite:///data.db'
# dashboard.config.database_name = 'mysql+pymysql://user:password@localhost:3306/db1'
# dashboard.config.database_name = 'postgresql://user:password@localhost:5432/mydb'
dashboard.bind(app)


@app.route('/endpointd')
def endpoint():
    print("Hello, world")
    return 'Ok2d'


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

# schedule = {'weeks': 0,
#             'days': 0,
#             'hours': 1,
#             'minutes': 30,
#             'seconds': 0}
#
# dashboard.add_graph('Graph1', lambda: my_func(), **schedule)
