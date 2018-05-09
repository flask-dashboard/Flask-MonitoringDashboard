from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import boxplot, get_figure, get_layout, get_margin
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions


TITLE = 'Per-Version Performance'

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents the versions 
that are used.'''

CONTENT_INFO = '''This graph shows a horizontal boxplot for the versions that are used. With this
graph you can found out whether the performance changes across different versions.'''


@blueprint.route('/endpoint/<end>/versions', methods=['GET', 'POST'])
@secure
def versions(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
    graph = versions_graph(end)
    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph,
                           title='{} for {}'.format(TITLE, end),
                           information=get_information(AXES_INFO, CONTENT_INFO))


def versions_graph(end):
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
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'Version', 'autorange': 'reversed'},
        margin=get_margin()
    )
    return get_figure(layout=layout, data=data)
