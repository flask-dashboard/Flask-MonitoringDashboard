import datetime

from flask import request

import flask_monitoringdashboard.views.export.csv
import flask_monitoringdashboard.views.export.json
from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.tests import add_test_result
from flask_monitoringdashboard.database.tests_grouped import reset_tests_grouped, add_tests_grouped


@blueprint.route('/submit-test-results', methods=['POST'])
def submit_test_results():
    """
    Endpoint for letting Travis submit its unit test performance results to the Dashboard.
    :return: nothing, 204 (No Content)
    """
    json_str = request.get_json()
    suite = int(float(json_str['travis_job']))
    app_version = '-1'
    if 'app_version' in json_str:
        app_version = json_str['app_version']
    content = request.get_json()['test_runs']
    with session_scope() as db_session:
        for result in content:
            time = datetime.datetime.strptime(result['time'], '%Y-%m-%d %H:%M:%S.%f')
            add_test_result(db_session, result['name'], result['exec_time'], time, app_version, suite,
                            result['iter'])

        groups = request.get_json()['grouped_tests']
        if groups:
            reset_tests_grouped(db_session)
            add_tests_grouped(db_session, groups)

    return '', 204
