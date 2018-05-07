from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot, get_margin
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.core.utils import simplify
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.function_calls import get_endpoints, get_data_per_endpoint

TITLE = 'Global execution time for every endpoint'

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents every
endpoint of the Flask application.'''

CONTENT_INFO = '''In this graph, it is easy to compare the execution time of the different endpoints
across each other. This information can be used to validate which endpoints needs to be improved.'''


@blueprint.route('/endpoints')
@secure
def endpoints():
    return render_template('fmd_dashboard/graph.html', graph=endpoint_graph(), title=TITLE,
                           information=get_information(AXES_INFO, CONTENT_INFO))


def endpoint_graph():
    """
    Creates a graph with the execution times per endpoint
    :return:
    """
    with session_scope() as db_session:
        endpoints = get_endpoints(db_session)

        data = []
        for endpoint in endpoints:
            values = [c.execution_time for c in get_data_per_endpoint(db_session, endpoint)]
            if values:
                data.append(boxplot(simplify(values, 10), name=endpoint))

    layout = get_layout(
        height=350 + 40 * len(endpoints),
        xaxis={'title': 'Execution time (ms)'},
        margin=get_margin()
    )
    return get_figure(layout, data)
