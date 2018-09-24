import datetime

from flask import make_response

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.outlier import get_all_outliers
from flask_monitoringdashboard.database.request import get_data

REQUESTS_COLUMNS = ['id', 'endpoint_id', 'duration', 'time_requested',
                    'version_requested', 'group_by', 'ip']
OUTLIER_COLUMNS = ['id', 'request_id', 'request_header', 'request_environment',
                   'request_url', 'cpu_percent', 'memory', 'stacktrace']


@blueprint.route('/download-requests')
@admin_secure
def download_requests():
    csv = ','.join(REQUESTS_COLUMNS) + '\n'
    with session_scope() as db_session:
        for entry in get_data(db_session):
            csv += ','.join([str(entry.__getattribute__(c)) for c in REQUESTS_COLUMNS]) + '\n'

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=requests_{0}.csv".format(
        str(datetime.datetime.utcnow()).replace(" ", "_").replace(":", "-")[:19])
    return response


@blueprint.route('/download-outliers')
@admin_secure
def download_outliers():
    csv = ','.join(OUTLIER_COLUMNS) + '\n'
    with session_scope() as db_session:
        for entry in get_all_outliers(db_session):
            data = ','.join([str(entry.__getattribute__(c)) for c in OUTLIER_COLUMNS])
            data = ' '.join(data.split())  # remove newlines
            csv += data + '\n'

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=outliers_{0}.csv".format(
        str(datetime.datetime.utcnow()).replace(" ", "_").replace(":", "-")[:19])
    return response
