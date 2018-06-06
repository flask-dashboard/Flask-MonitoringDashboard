from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, get_margin, heatmap
from flask_monitoringdashboard.core.info_box import get_plot_info
from flask_monitoringdashboard.database import Request, session_scope
from flask_monitoringdashboard.database.count import count_versions
from flask_monitoringdashboard.database.count_group import count_requests_group, get_value
from flask_monitoringdashboard.database.endpoint import get_endpoints
from flask_monitoringdashboard.database.versions import get_versions

TITLE = 'Multi Version API Utilization'

AXES_INFO = '''The X-axis presents the versions that are used. The Y-axis presents the 
endpoints that are found in the Flask application.'''

CONTENT_INFO = '''The color of the cell presents the distribution of the amount of requests that the 
application received in a single version for a single endpoint. The darker the cell, the more requests 
a certain endpoint has processed in that version. Since it displays the distribution of the load, each 
column sums up to 100%. This information can be used to validate which endpoints processes the most 
requests.'''


@blueprint.route('/version_usage', methods=['GET', 'POST'])
@secure
def version_usage():
    with session_scope() as db_session:
        form = get_slider_form(count_versions(db_session), 'Select the number of versions')
        graph = version_usage_graph(db_session, form)
    return render_template('fmd_dashboard/graph.html', graph=graph, title=TITLE,
                           information=get_plot_info(AXES_INFO, CONTENT_INFO), form=form)


def version_usage_graph(db_session, form):
    """
    Used for getting a Heatmap with an overview of which endpoints are used in which versions
    :param db_session: session for the database
    :param form: instance of SliderForm
    :return:
    """
    endpoints = get_endpoints(db_session)
    versions = get_versions(db_session, limit=form.get_slider_value())

    requests = [count_requests_group(db_session, Request.version_requested == v) for v in versions]
    total_hits = []
    hits = [[]] * len(endpoints)

    for hits_version in requests:
        total_hits.append(max(1, sum([value for key, value in hits_version])))

    for j in range(len(endpoints)):
        hits[j] = [0] * len(versions)
        for i in range(len(versions)):
            hits[j][i] = get_value(requests[i], endpoints[j].id) * 100 / total_hits[i]

    layout = get_layout(
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin()
    )

    trace = heatmap(
        z=hits,
        x=versions,
        y=['{} '.format(e.name) for e in endpoints],
        colorbar={
            'titleside': 'top',
            'tickmode': 'array',
        }
    )
    return get_figure(layout=layout, data=[trace])
