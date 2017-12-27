from flask import make_response, render_template, session, request, jsonify
from dashboard.security import admin_secure
from dashboard.database.function_calls import get_data, get_data_from
from dashboard.database.tests import add_or_update_test, add_test_result, get_suite_nr
from dashboard.database.tests_grouped import reset_tests_grouped, add_tests_grouped
from dashboard import blueprint, config

import datetime


@blueprint.route('/download-csv')
@admin_secure
def download_csv():
    csv = "\"ENDPOINT\",\"EXECUTION_TIME\",\"TIME_OF_EXECUTION\",\"VERSION\",\"GROUP_BY\",\"IP_ADDRESS\"\n"
    for entry in get_data():
        csv += "\"{0}\",{1},\"{2}\",\"{3}\",\"{4}\",\"{5}\"\n".format(
            entry.endpoint, entry.execution_time, entry.time, entry.version, entry.group_by, entry.ip)

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=measurements_{0}.csv".format(
        str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")[:19])
    return response


@blueprint.route('/export-data')
@admin_secure
def export_data():
    csv = ["\"ENDPOINT\",\"EXECUTION_TIME\",\"TIME_OF_EXECUTION\",\"VERSION\",\"GROUP_BY\",\"IP_ADDRESS\""]
    data = get_data()
    for entry in data:
        csv.append("\"{0}\",{1},\"{2}\",\"{3}\",\"{4}\",\"{5}\"".format(entry.endpoint, entry.execution_time,
                                                                        entry.time, entry.version, entry.group_by,
                                                                        entry.ip))
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


@blueprint.route('/get_json_data/<security_token>', defaults={'time_from': 0})
@blueprint.route('/get_json_data/<security_token>/<time_from>')
def get_json_data_from(security_token: str, time_from: int):
    """
    Only get the data if the security token with the request is equivalent to the security token in the configuration.
    :param security_token: security token to be specified.
    :param time_from: (optional) if specified, only the data-values after this date are returned.
                      input must be an timestamp value (utc) (= integer)
    :return: all entries from the database.
    """
    if security_token == config.security_token:
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
            return 'ValueError: {0}'.format(e)
    return jsonify()
