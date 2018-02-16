from functools import wraps

from flask import make_response, render_template, session, request, jsonify

from dashboard.database.monitor_rules import get_monitor_data
from dashboard.security import admin_secure
from dashboard.database.function_calls import get_data, get_data_from
from dashboard.database.tests import add_or_update_test, add_test_result, get_suite_nr
from dashboard.database.tests_grouped import reset_tests_grouped, add_tests_grouped
from dashboard import blueprint, config

import datetime


@blueprint.route('/download-csv')
@admin_secure
def download_csv():
    csv = '"ENDPOINT","EXECUTION_TIME","TIME_OF_EXECUTION","VERSION","GROUP_BY","IP_ADDRESS"\n'
    for entry in get_data():
        csv += '"{}",{},"{}","{}","{}","{}"\n'.format(entry.endpoint, entry.execution_time, entry.time, entry.version,
                                                      entry.group_by, entry.ip)

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=measurements_{0}.csv".format(
        str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")[:19])
    return response


@blueprint.route('/export-data')
@admin_secure
def export_data():
    csv = ['"ENDPOINT","EXECUTION_TIME","TIME_OF_EXECUTION","VERSION","GROUP_BY","IP_ADDRESS"']
    data = get_data()
    for entry in data:
        csv.append('"{}","{}","{}","{}","{}","{}"'.format(entry.endpoint, entry.execution_time, entry.time,
                                                          entry.version, entry.group_by, entry.ip))
    return render_template('dashboard/export-data.html', link=config.link, session=session, data=csv)


@blueprint.route('/submit-test-results', methods=['POST'])
def submit_test_results():
    content = request.get_json()['test_runs']
    suite = get_suite_nr()
    for result in content:
        time = datetime.datetime.strptime(result['time'], '%Y-%m-%d %H:%M:%S.%f')
        add_or_update_test(result['name'], time, result['successful'])
        add_test_result(result['name'], result['exec_time'], time, config.version, suite, result['iter'])

    groups = request.get_json()['grouped_tests']
    if groups:
        reset_tests_grouped()
        add_tests_grouped(groups)

    return '', 204


def check_security_token(func):
    """
        Checks if the security_token that is provided in the route-function, is equivalent to the security_token in the
        configuration file. For example. If the rule of the endpoint is: /endpoint/<security_token> and the actual
        request is: /endpoint/1234, then request.view_args.get('security_token', '') returns '1234'
        This function can be used as a decorator, to verify the security_token. If the verification fails, an empty
        json-string is returned.
    :param func: the endpoint to be wrapped. Note that the endpoint must have a rule of the form:
    '.../<security_token>...' otherwise this decorator doesn't make sense.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if config and config.security_token == request.view_args.get('security_token', ''):
            return func(*args, **kwargs)
        return jsonify()

    return wrapper


@blueprint.route('/get_json_data/<security_token>', defaults={'time_from': 0})
@blueprint.route('/get_json_data/<security_token>/<time_from>')
@check_security_token
def get_json_data_from(security_token: str, time_from: int):
    """
    Only get the data if the security token with the request is equivalent to the security token in the configuration.
    :param security_token: security token to be specified.
    :param time_from: (optional) if specified, only the data-values after this date are returned.
                      input must be an timestamp value (utc) (= integer)
    :return: all entries from the database. (endpoint-table)
    """
    data = []
    try:
        for entry in get_data_from(datetime.datetime.utcfromtimestamp(int(time_from))):
            # nice conversion to json-object
            data.append({
                'endpoint': entry.endpoint,
                'execution_time': entry.execution_time,
                'time': str(entry.time),
                'version': entry.version,
                'group_by': entry.group_by,
                'ip': entry.ip
            })
        return jsonify(data)
    except ValueError as e:
        return 'ValueError: {}'.format(e)


@blueprint.route('/get_json_monitor_rules/<security_token>')
@check_security_token
def get_json_monitor_rules(security_token: str):
    """
    Only get the data if the security token with the request is equivalent to the security token in the configuration.
    :param security_token: security token for accessing the data
    :return: all entries from the database (rules-table)
    """
    data = []
    try:
        for entry in get_monitor_data():
            # nice conversion to json-object
            data.append({
                'endpoint': entry.endpoint,
                'last_accessed': str(entry.last_accessed),
                'monitor': entry.monitor,
                'time_added': str(entry.time_added),
                'version_added': entry.version_added
            })
        return jsonify(data)
    except ValueError as e:
        return 'ValueError: {}'.format(e)
