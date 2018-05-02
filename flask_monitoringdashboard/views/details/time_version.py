from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions


@blueprint.route('/result/<end>/time_per_version', methods=['GET', 'POST'])
@secure
def result_time_per_version(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
    graph = get_time_per_version(end)
    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph)


def get_time_per_version(end):
    data = []
    with session_scope() as db_session:
        versions = get_versions(db_session, end=end)
        for version in versions:
            values = [str(c.execution_time) for c in
                      get_all_measurement_per_column(db_session, endpoint=end, column=FunctionCall.version,
                                                     value=version)]
            name = "{} {}".format(version, get_date_first_request(db_session, version).strftime("%b %d %H:%M"))
            data.append(boxplot(values=values, name=name))

    layout = get_layout(
        height=350 + 40 * len(versions),
        title='Execution time for every version',
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'Version', 'autorange': 'reversed'},
        margin=get_margin()
    )
    return get_figure(layout=layout, data=data)
