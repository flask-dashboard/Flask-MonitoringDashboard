from flask import make_response, render_template, session, request, redirect, url_for
from dashboard.security import secure
from dashboard.database.function_calls import get_data
from dashboard.database.tests import add_or_update_test, add_test_result, get_suite_nr
from dashboard import blueprint, config

import datetime


@blueprint.route('/download-csv')
@secure
def download_csv():
    csv = "\"ENDPOINT\",\"EXECUTION_TIME\",\"TIME_OF_EXECUTION\",\"VERSION\",\"GROUP_BY\",\"IP_ADDRESS\"\n"
    data = get_data()
    for entry in data:
        csv += "\"{0}\",{1},\"{2}\",\"{3}\",\"{4}\",\"{5}\"\n".format(entry.endpoint, entry.execution_time, entry.time,
                                                                      entry.version, entry.group_by, entry.ip)

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=measurements_{0}.csv".format(
        str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")[:19])
    return response


@blueprint.route('/export-data')
@secure
def export_data():
    csv = ["\"ENDPOINT\",\"EXECUTION_TIME\",\"TIME_OF_EXECUTION\",\"VERSION\",\"GROUP_BY\",\"IP_ADDRESS\""]
    data = get_data()
    for entry in data:
        csv.append("\"{0}\",{1},\"{2}\",\"{3}\",\"{4}\",\"{5}\"".format(entry.endpoint, entry.execution_time,
                                                                        entry.time, entry.version, entry.group_by,
                                                                        entry.ip))

    return render_template('export-data.html', link=config.link, session=session, data=csv)


@blueprint.route('/submit-test-results', methods=['POST'])
def submit_test_results():
    content = request.get_json()['test_runs']
    suite = get_suite_nr()
    for result in content:
        time = datetime.datetime.strptime(result['time'], '%Y-%m-%d %H:%M:%S.%f')
        add_or_update_test(result['name'], time, result['successful'])
        add_test_result(result['name'], result['exec_time'], time, config.version, suite, result['iter'])
    return '', 204
