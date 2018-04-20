from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column, get_num_versions
from flask_monitoringdashboard.database.versions import get_date_first_request
from flask_monitoringdashboard.database.function_calls import get_versions
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/time_per_version', methods=['GET', 'POST'])
@secure
def result_time_per_version(end):
    form = get_slider_form(get_num_versions(end))
    graph = get_time_per_version(end, form)
    return render_template('endpoint/time_per_user.html', details=get_endpoint_details(end), form=form, graph=graph)


def get_time_per_version(end, form):
    limit = form.get_slider_value()
    data = []
    versions = get_versions(end=end, limit=limit)
    for version in versions:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.version, value=version)]
        name = "{} {}".format(version, get_date_first_request(version).strftime("%b %d %H:%M"))
        data.append(boxplot(values=values, name=name))

    layout = get_layout(
        height=350 + 40 * len(versions),
        title='Execution time for every version',
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'title': 'Version', 'autorange': 'reversed'},
        margin=get_margin()
    )
    return get_figure(layout=layout, data=data)
