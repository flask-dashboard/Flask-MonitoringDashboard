import datetime
import jwt
import pkg_resources

from flask import make_response, render_template, session, request, json, jsonify

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.database.function_calls import get_data, get_data_from
from flask_monitoringdashboard.database.monitor_rules import get_monitor_data
from flask_monitoringdashboard.database.tests import add_or_update_test, add_test_result, get_suite_nr
from flask_monitoringdashboard.database.tests_grouped import reset_tests_grouped, add_tests_grouped
from flask_monitoringdashboard.security import admin_secure
# from setup import VERSION

CSV_COLUMNS = ['endpoint', 'execution_time', 'time', 'version', 'group_by', 'ip']


@blueprint.route('/download-csv')
@admin_secure
def download_csv():
    csv = ','.join(CSV_COLUMNS) + '\n'
    for entry in get_data():
        csv += ','.join([str(entry.__getattribute__(c)) for c in CSV_COLUMNS]) + '\n'

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=measurements_{0}.csv".format(
        str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")[:19])
    return response


@blueprint.route('/export-data')
@admin_secure
def export_data():
    csv = [','.join(CSV_COLUMNS)]
    data = get_data()
    for entry in data:
        csv.append(','.join([str(entry.__getattribute__(c)) for c in CSV_COLUMNS]) + '\n')
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


@blueprint.route('/get_json_data', defaults={'time_from': 0})
@blueprint.route('/get_json_data/<time_from>')
def get_json_data_from(time_from):
    """
    The returned data is the data that is encrypted using a security token. This security token is set in the
    configuration.
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
        return jwt.encode({'data': json.dumps(data)}, config.security_token, algorithm='HS256')
    except ValueError as e:
        return 'ValueError: {}'.format(e)


@blueprint.route('/get_json_monitor_rules')
def get_json_monitor_rules():
    """
    The returned data is the data that is encrypted using a security token. This security token is set in the
    configuration.
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
        return jwt.encode({'data': json.dumps(data)}, config.security_token, algorithm='HS256')
    except ValueError as e:
        return 'ValueError: {}'.format(e)


@blueprint.route('/get_json_details')
def get_json_details():
    """
    Some details about the deployment, such as the current version, etc...
    :return: a json-object with the details.
    """
    version = pkg_resources.require("Flask-MonitoringDashboard")[0].version
    return jsonify({'version': version})
