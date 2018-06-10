import datetime

from flask import request

import flask_monitoringdashboard.views.export.csv
import flask_monitoringdashboard.views.export.json
from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.tested_endpoints import add_endpoint_hit
from flask_monitoringdashboard.database.tests import add_test_result, add_or_update_test


@blueprint.route('/submit-test-results', methods=['POST'])
def submit_test_results():
    """
    Endpoint for letting Travis submit its unit test performance results to the Dashboard.
    :return: nothing, 204 (No Content)
    """
    results = request.get_json()
    travis_job_id = -1
    if results['travis_job']:
        travis_job_id = results['travis_job']
    app_version = '-1'
    if 'app_version' in results:
        app_version = results['app_version']
    test_runs = results['test_runs']
    endpoint_hits = results['endpoint_exec_times']

    with session_scope() as db_session:
        for test_run in test_runs:
            time = datetime.datetime.strptime(test_run['time'], '%Y-%m-%d %H:%M:%S.%f')
            add_or_update_test(db_session, test_run['name'], test_run['successful'], time, app_version)
            add_test_result(db_session, test_run['name'], test_run['exec_time'], time, app_version,
                            travis_job_id, test_run['iter'])

        for endpoint_hit in endpoint_hits:
            add_endpoint_hit(db_session, endpoint_hit['endpoint'], endpoint_hit['exec_time'], endpoint_hit['test_name'],
                             app_version, travis_job_id)

    return '', 204
