import math

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import scatter, get_figure, get_margin, get_layout, get_average_bubble_size
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.core.utils import get_endpoint_details, formatter
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count import count_users
from flask_monitoringdashboard.database.endpoint import get_group_by_sorted
from flask_monitoringdashboard.database.function_calls import get_median
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions

TITLE = 'User-Focused Multi-Version Performance'

AXES_INFO = '''In this graph, the X-axis presents the versions that are used. The Y-axis presents
(a subset of) all unique users, as specified by "dashboard.config.group_by". You can use the slider
to select a subset of the all unique users.'''

CONTENT_INFO = '''A circle represents the median execution time of a unique user in a certain version.
A larger execution time is presented by a larger circle. With this graph you can find out whether
there is a difference in performance across users.'''


@blueprint.route('/endpoint/<end>/version_user', methods=['GET', 'POST'])
@secure
def version_user(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        form = get_slider_form(count_users(db_session, end))
    graph = version_user_graph(end, form)
    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph, form=form,
                           title='{} for {}'.format(TITLE, end),
                           information=get_information(AXES_INFO, CONTENT_INFO))


def version_user_graph(end, form):
    with session_scope() as db_session:
        group_by_list = get_group_by_sorted(db_session, end, form.get_slider_value())
        versions = get_versions(db_session, end)

        data = []
        for group_by in group_by_list:
            data.append(
                [get_median(db_session, end, FunctionCall.version == v, FunctionCall.group_by == group_by) for v in
                 versions])
        average = get_average_bubble_size(data)

        trace = []
        for i in range(len(group_by_list)):
            hovertext = ['Version: {}<br>Time: {}'.format(versions[j], formatter(data[i][j])) for j in
                         range(len(versions))]
            trace.append(scatter(
                x=['{}<br>{}'.format(v, get_date_first_request(db_session, v).strftime('%b %d %H:%M')) for v in
                   versions],
                hovertext=hovertext,
                y=[group_by_list[i]] * len(versions),
                name=group_by_list[i],
                mode='markers',
                marker={
                    'color': [get_color(group_by_list[i])] * len(versions),
                    'size': [math.sqrt(d) for d in data[i]],
                    'sizeref': average,
                    'sizemode': 'area'
                }
            ))

    layout = get_layout(
        height=350 + 40 * len(trace),
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'title': 'Users', 'type': 'category', 'autorange': 'reversed'},
        margin=get_margin(b=200)
    )
    return get_figure(layout, trace)
