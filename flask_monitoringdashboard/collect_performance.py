import requests
import configparser
import time
import datetime
import os
import sys
import csv
from unittest import TestLoader

# Abort if config file is not specified.
config = os.getenv('DASHBOARD_CONFIG')
if config is None:
    print('You must specify a config file for the dashboard to be able to use the unit test monitoring functionality.')
    print('Please set an environment variable \'DASHBOARD_CONFIG\' specifying the absolute path to your config file.')
    sys.exit(0)

# Abort if log directory is not specified.
log_dir = os.getenv('DASHBOARD_LOG_DIR')
if log_dir is None:
    print('You must specify a log directory for the dashboard to be able to use the unit test monitoring '
          'functionality.')
    print('Please set an environment variable \'DASHBOARD_LOG_DIR\' specifying the absolute path where you want the '
          'log files to be placed.')
    sys.exit(0)

n = 1
url = None
sys.path.insert(0, os.getcwd())
parser = configparser.RawConfigParser()
try:
    parser.read(config)
    if parser.has_option('dashboard', 'N'):
        n = int(parser.get('dashboard', 'N'))
    if parser.has_option('dashboard', 'TEST_DIR'):
        test_dir = parser.get('dashboard', 'TEST_DIR')
    else:
        print('No test directory specified in your config file. Please do so.')
        sys.exit(0)
    if parser.has_option('dashboard', 'SUBMIT_RESULTS_URL'):
        url = parser.get('dashboard', 'SUBMIT_RESULTS_URL')
    else:
        print('No url specified in your config file for submitting test results. Please do so.')
except configparser.Error as e:
    print("Something went wrong while parsing the configuration file:\n{}".format(e))

data = {'test_runs': [], 'grouped_tests': []}
log = open(log_dir + "endpoint_hits.log", "w")
log.write("\"time\",\"endpoint\"\n")
log.close()
log = open(log_dir + "test_runs.log", "w")
log.write("\"start_time\",\"stop_time\",\"test_name\"\n")

if test_dir:
    suites = TestLoader().discover(test_dir, pattern="*test*.py")
    for i in range(n):
        for suite in suites:
            for case in suite:
                for test in case:
                    result = None
                    t1 = str(datetime.datetime.now())
                    time1 = time.time()
                    result = test.run(result)
                    time2 = time.time()
                    t2 = str(datetime.datetime.now())
                    log.write("\"{}\",\"{}\",\"{}\"\n".format(t1, t2, str(test)))
                    t = (time2 - time1) * 1000
                    data['test_runs'].append({'name': str(test), 'exec_time': t, 'time': str(datetime.datetime.now()),
                                              'successful': result.wasSuccessful(), 'iter': i + 1})

log.close()

# Read and parse the log containing the test runs
runs = []
with open(log_dir + 'test_runs.log') as log:
    reader = csv.DictReader(log)
    for row in reader:
        runs.append([datetime.datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S.%f"),
                     datetime.datetime.strptime(row["stop_time"], "%Y-%m-%d %H:%M:%S.%f"),
                     row['test_name']])

# Read and parse the log containing the endpoint hits
hits = []
with open(log_dir + 'endpoint_hits.log') as log:
    reader = csv.DictReader(log)
    for row in reader:
        hits.append([datetime.datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S.%f"),
                     row['endpoint']])

# Analyze logs to find out which endpoints are hit by which unit tests
for h in hits:
    for r in runs:
        if r[0] <= h[0] <= r[1]:
            if {'endpoint': h[1], 'test_name': r[2]} not in data['grouped_tests']:
                data['grouped_tests'].append({'endpoint': h[1], 'test_name': r[2]})
            break

# Try to send test results and endpoint-grouped unit tests to the flask_monitoringdashboard
if url:
    try:
        requests.post(url, json=data)
        print('Sent unit test results to the dashboard.')
    except Exception as e:
        print('Sending unit test results to the dashboard failed:\n{}'.format(e))
