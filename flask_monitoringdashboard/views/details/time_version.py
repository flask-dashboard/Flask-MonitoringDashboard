from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions
from flask_monitoringdashboard.core.utils import get_endpoint_details


@blueprint.route('/result/<end>/time_per_version', methods=['GET', 'POST'])
@secure
def result_time_per_version(end):
    graph = get_time_per_version(end)
    return render_template('dashboard/graph-details.html', details=get_endpoint_details(end), graph=graph)


def get_time_per_version(end):
    data = []
    versions = get_versions(end=end)
    for version in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=version)]
        name = "{} {}".format(version, get_date_first_request(version).strftime("%b %d %H:%M"))
        data.append(boxplot(values=values, name=name))

    layout = get_layout(
        height=350 + 40 * len(versions),
        title='Execution time for every version',
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'Version', 'autorange': 'reversed'},
        margin=get_margin()
    )
    return get_figure(layout=layout, data=data)
