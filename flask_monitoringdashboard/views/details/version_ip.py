import math

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_average_bubble_size, scatter, get_layout, get_margin, get_figure
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.core.utils import get_endpoint_details, formatter
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count import count_ip
from flask_monitoringdashboard.database.endpoint import get_ip_sorted
from flask_monitoringdashboard.database.function_calls import get_median
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions


TITLE = 'IP-Focused Multi-Version Performance'

AXES_INFO = '''In this graph, the X-axis presents the versions that are used. The Y-axis presents
(a subset of) all IP-addresses. You can use the slider to select a subset of the all IP-addresses.'''

CONTENT_INFO = '''A circle represents the median execution time of the requests from a unique IP-
address in a certain version. A larger execution time is presented by a larger circle. With this 
graph you don\'t need any configuration to see a difference between the performance of different 
IP-addresses.'''


@blueprint.route('/endpoint/<end>/version_ip', methods=['GET', 'POST'])
@secure
def version_ip(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        form = get_slider_form(count_ip(db_session, end))
    graph = version_ip_graph(end, form)
    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph, form=form,
                           title='{} for {}'.format(TITLE, end),
                           information=get_information(AXES_INFO, CONTENT_INFO))


def version_ip_graph(end, form):
    with session_scope() as db_session:
        ip_list = get_ip_sorted(db_session, end, form.get_slider_value())
        versions = get_versions(db_session, end)

        data = []
        for ip in ip_list:
            data.append(
                [get_median(db_session, end, FunctionCall.version == v, FunctionCall.ip == ip) for v in versions])
        average = get_average_bubble_size(data)
        trace = []
        for i in range(len(ip_list)):
            hovertext = ['Version: {}<br>Time: {}'.format(versions[j], formatter(data[i][j])) for j in
                         range(len(versions))]
            trace.append(scatter(
                x=['{}<br>{}'.format(v, get_date_first_request(db_session, v).strftime('%b %d %H:%M')) for v in
                   versions],
                hovertext=hovertext,
                y=[ip_list[i]] * len(versions),
                name=ip_list[i],
                mode='markers',
                marker={
                    'color': [get_color(ip_list[i])] * len(versions),
                    'size': [math.sqrt(d) for d in data[i]],
                    'sizeref': average,
                    'sizemode': 'area'
                }
            ))

    layout = get_layout(
        height=350 + 40 * len(trace),
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin(b=200)
    )
    return get_figure(layout, trace)
