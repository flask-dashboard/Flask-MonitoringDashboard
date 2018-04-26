from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.utils import simplify
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import boxplot, get_layout, get_figure, get_margin
from flask_monitoringdashboard.database.function_calls import get_data_per_version
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions

TITLE = 'Global execution time for every version'


@blueprint.route('/measurements/versions')
@secure
def page_boxplot_per_version():
    return render_template('dashboard/graph.html', graph=get_boxplot_per_version(), title=TITLE)


def get_boxplot_per_version():
    """
    Creates a graph with the execution times per version
    :return:
    """
    versions = get_versions()

    if not versions:
        return None

    data = []
    for version in versions:
        values = [c.execution_time for c in get_data_per_version(version)]
        name = "{} {}".format(version, get_date_first_request(version).strftime("%b %d %H:%M"))
        data.append(boxplot(name=name, values=simplify(values, 10), marker={'color': get_color(version)}))

    layout = get_layout(
        height=350 + 40 * len(versions),
        title=TITLE,
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin()
    )
    return get_figure(layout=layout, data=data)
