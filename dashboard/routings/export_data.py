from flask import make_response, render_template, session
from dashboard.security import secure
from dashboard.database.function_calls import get_data
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

    return render_template('dashboard/export-data.html', link=config.link, session=session, data=csv)
