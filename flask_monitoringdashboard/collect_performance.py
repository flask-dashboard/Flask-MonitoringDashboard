import argparse
import csv
import datetime
import time
from unittest import TestLoader

import requests

# Parsing the arguments.
parser = argparse.ArgumentParser(description='Collecting performance results from the unit tests of a project.')
parser.add_argument('--test_folder', dest='test_folder', required=True,
                    help='folder in which the unit tests can be found (example: ./tests)')
parser.add_argument('--times', dest='times', default=5,
                    help='number of times to execute every unit test (default: 5)')
parser.add_argument('--url', dest='url', default=None,
                    help='url of the Dashboard to submit the performance results to')
args = parser.parse_args()
print('Starting the collection of performance results with the following settings:')
print('  - folder containing unit tests: ', args.test_folder)
print('  - number of times to run tests: ', args.times)
print('  - url to submit the results to: ', args.url)
if not args.url:
    print('The performance results will not be submitted.')

# Initialize result dictionary and logs.
data = {'test_runs': [], 'grouped_tests': []}
log = open('endpoint_hits.log', 'w')
log.write('"time","endpoint"\n')
log.close()
log = open('test_runs.log', 'w')
log.write('"start_time","stop_time","test_name"\n')

# Find the tests and execute them the specified number of times.
# Add the performance results to the result dictionary.
suites = TestLoader().discover(args.test_folder, pattern="*test*.py")
for iteration in range(args.times):
    for suite in suites:
        for case in suite:
            for test in case:
                test_result = None
                start_time_stamp = str(datetime.datetime.now())
                time_before = time.time()
                test_result = test.run(test_result)
                time_after = time.time()
                end_time_stamp = str(datetime.datetime.now())
                log.write('"{}","{}","{}"\n'.format(start_time_stamp, end_time_stamp, str(test)))
                execution_time = (time_after - time_before) * 1000
                data['test_runs'].append(
                    {'name': str(test), 'exec_time': execution_time, 'time': str(datetime.datetime.now()),
                     'successful': test_result.wasSuccessful(), 'iter': iteration + 1})
log.close()

# Read and parse the log containing the test runs into an array for processing.
test_runs = []
with open('test_runs.log') as log:
    reader = csv.DictReader(log)
    for row in reader:
        test_runs.append([datetime.datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S.%f"),
                          datetime.datetime.strptime(row["stop_time"], "%Y-%m-%d %H:%M:%S.%f"),
                          row['test_name']])

# Read and parse the log containing the endpoint hits into an array for processing.
endpoint_hits = []
with open('endpoint_hits.log') as log:
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

# Send test results and endpoint_name/test_name combinations to the Dashboard if specified.
if args.url:
    if args.url[-1] == '/':
        args.url += 'submit-test-results'
    else:
        args.url += '/submit-test-results'
    try:
        requests.post(args.url, json=data)
        print('Sent unit test results to the Dashboard at ', args.url)
    except Exception as e:
        print('Sending unit test results to the dashboard failed:\n{}'.format(e))
