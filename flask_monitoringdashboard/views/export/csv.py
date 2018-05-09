import datetime

from flask import make_response, render_template, session

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.function_calls import get_data

CSV_COLUMNS = ['endpoint', 'execution_time', 'time', 'version', 'group_by', 'ip']


@blueprint.route('/download-csv')
@admin_secure
def download_csv():
    csv = ','.join(CSV_COLUMNS) + '\n'
    with session_scope() as db_session:
        for entry in get_data(db_session):
            csv += ','.join([str(entry.__getattribute__(c)) for c in CSV_COLUMNS]) + '\n'

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=measurements_{0}.csv".format(
        str(datetime.datetime.utcnow()).replace(" ", "_").replace(":", "-")[:19])
    return response


@blueprint.route('/view-csv')
@admin_secure
def view_csv():
    csv = [','.join(CSV_COLUMNS)]
    with session_scope() as db_session:
        for entry in get_data(db_session):
            csv.append(','.join([str(entry.__getattribute__(c)) for c in CSV_COLUMNS]) + '\n')
    return render_template('fmd_export-data.html', data=csv)
