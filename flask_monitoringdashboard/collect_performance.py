import argparse
import csv
import datetime
import os
import time
from unittest import TestLoader

import requests

# Determine if this script was called normally or if the call was part of a unit test on Travis.
# When unit testing, only run one dummy test from the testmonitor folder and submit to a dummy url.
test_folder = os.getcwd() + '/flask_monitoringdashboard/test/views/testmonitor'
times = '1'
url = 'https://httpbin.org/post'
if 'flask-dashboard/Flask-MonitoringDashboard' not in os.getenv('TRAVIS_BUILD_DIR'):
    parser = argparse.ArgumentParser(description='Collecting performance results from the unit tests of a project.')
    parser.add_argument('--test_folder', dest='test_folder', default='./',
                        help='folder in which the unit tests can be found (default: ./)')
    parser.add_argument('--times', dest='times', default=5,
                        help='number of times to execute every unit test (default: 5)')
    parser.add_argument('--url', dest='url', default=None,
                        help='url of the Dashboard to submit the performance results to')
    args = parser.parse_args()
    test_folder = args.test_folder
    times = args.times
    url = args.url

# Show the settings with which this script will run.
print('Starting the collection of performance results with the following settings:')
print('  - folder containing unit tests: ', test_folder)
print('  - number of times to run tests: ', times)
print('  - url to submit the results to: ', url)
if not url:
    print('The performance results will not be submitted.')

# Initialize result dictionary and logs.
data = {'test_runs': [], 'grouped_tests': []}
home = os.path.expanduser("~")
log = open(home + '/endpoint_hits.log', 'w')
log.write('"time","endpoint"\n')
log.close()
log = open(home + '/test_runs.log', 'w')
log.write('"start_time","stop_time","test_name"\n')

# Find the tests and execute them the specified number of times.
# Add the performance results to the result dictionary.
suites = TestLoader().discover(test_folder, pattern="*test*.py")
for iteration in range(int(times)):
    for suite in suites:
        for case in suite:
            for test in case:
                test_result = None
                start_time_stamp = str(datetime.datetime.utcnow())
                time_before = time.time()
                test_result = test.run(test_result)
                time_after = time.time()
                end_time_stamp = str(datetime.datetime.utcnow())
                log.write('"{}","{}","{}"\n'.format(start_time_stamp, end_time_stamp, str(test)))
                execution_time = (time_after - time_before) * 1000
                data['test_runs'].append(
                    {'name': str(test), 'exec_time': execution_time, 'time': str(datetime.datetime.utcnow()),
                     'successful': (test_result.wasSuccessful() if test_result else False), 'iter': iteration + 1})
log.close()

# Read and parse the log containing the test runs into an array for processing.
test_runs = []
with open(home + '/test_runs.log') as log:
    reader = csv.DictReader(log)
    for row in reader:
        test_runs.append([datetime.datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S.%f"),
                          datetime.datetime.strptime(row["stop_time"], "%Y-%m-%d %H:%M:%S.%f"),
                          row['test_name']])

# Read and parse the log containing the endpoint hits into an array for processing.
endpoint_hits = []
with open(home + '/endpoint_hits.log') as log:
    reader = csv.DictReader(log)
    for row in reader:
        endpoint_hits.append([datetime.datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S.%f"),
                              row['endpoint']])

# Analyze the two arrays to find out which endpoints were hit by which unit tests.
# Add the endpoint_name/test_name combination to the result dictionary.
for endpoint_hit in endpoint_hits:
    for test_run in test_runs:
        if test_run[0] <= endpoint_hit[0] <= test_run[1]:
            if {'endpoint': endpoint_hit[1], 'test_name': test_run[2]} not in data['grouped_tests']:
                data['grouped_tests'].append({'endpoint': endpoint_hit[1], 'test_name': test_run[2]})
            break

# Retrieve the current version of the user app that is being tested.
with open(home + '/app_version.log', 'r') as log:
    data['app_version'] = log.read()

# Add the current Travis Build Job number.
data['travis_job'] = os.getenv('TRAVIS_JOB_NUMBER')

# Send test results and endpoint_name/test_name combinations to the Dashboard if specified.
if url:
    if 'flask-dashboard/Flask-MonitoringDashboard' not in os.getenv('TRAVIS_BUILD_DIR'):
        if url[-1] == '/':
            url += 'submit-test-results'
        else:
            url += '/submit-test-results'
    try:
        requests.post(url, json=data)
        print('Sent unit test results to the Dashboard at', url)
    except Exception as e:
        print('Sending unit test results to the dashboard failed:\n{}'.format(e))
