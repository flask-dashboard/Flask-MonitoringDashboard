from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot, get_margin
from flask_monitoringdashboard.core.info_box import get_plot_info
from flask_monitoringdashboard.core.utils import simplify
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.data_grouped import get_endpoint_data_grouped
from flask_monitoringdashboard.database.endpoint import get_endpoints

TITLE = 'API Performance'

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents every
endpoint of the Flask application.'''

CONTENT_INFO = '''In this graph, it is easy to compare the execution time of the different endpoints
across each other. This information can be used to validate which endpoints needs to be improved.'''


@blueprint.route('/endpoints')
@secure
def endpoints():
    return render_template('fmd_dashboard/graph.html', graph=endpoint_graph(), title=TITLE,
                           information=get_plot_info(AXES_INFO, CONTENT_INFO))


def endpoint_graph():
    """
    Creates a graph with the execution times per endpoint
    :return:
    """
    with session_scope() as db_session:
        data = get_endpoint_data_grouped(db_session, lambda x: simplify(x, 10))
        values = [boxplot(get_value(data, end.id, default=[]), name=end.name)
                  for end in get_endpoints(db_session)]

    layout = get_layout(
        height=350 + 40 * len(values),
        xaxis={'title': 'Execution time (ms)'},
        margin=get_margin()
    )
    return get_figure(layout, values)
