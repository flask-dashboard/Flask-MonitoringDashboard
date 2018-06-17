import math

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.forms import get_double_slider_form
from flask_monitoringdashboard.core.plot import scatter, get_figure, get_margin, get_layout, get_average_bubble_size
from flask_monitoringdashboard.core.info_box import get_plot_info
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import Request, session_scope
from flask_monitoringdashboard.database.count import count_users, count_versions_endpoint
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.data_grouped import get_two_columns_grouped
from flask_monitoringdashboard.database.endpoint import get_users
from flask_monitoringdashboard.database.versions import get_versions, get_first_requests
from flask_monitoringdashboard.views.details.time_version import format_version

TITLE = 'User-Focused Multi-Version Performance'

AXES_INFO = '''In this graph, the X-axis presents the versions that are used. The Y-axis presents
(a subset of) all unique users, as specified by "dashboard.config.group_by". You can use the slider
to select a subset of the all unique users.'''

CONTENT_INFO = '''A circle represents the median execution time of a unique user in a certain version.
A larger execution time is presented by a larger circle. With this graph you can find out whether
there is a difference in performance across users.'''


FORM_SUBTITLE = ['Users', 'Versions']
FORM_TITLE = 'Select the number of users and versions'


@blueprint.route('/endpoint/<endpoint_id>/version_user', methods=['GET', 'POST'])
@secure
def version_user(endpoint_id):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, endpoint_id)

        slider_max = [count_users(db_session, endpoint_id), count_versions_endpoint(db_session, endpoint_id)]
        form = get_double_slider_form(slider_max, subtitle=FORM_SUBTITLE, title=FORM_TITLE)
        graph = version_user_graph(db_session, endpoint_id, form)
    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph, form=form,
                           title='{} for {}'.format(TITLE, details['endpoint']),
                           information=get_plot_info(AXES_INFO, CONTENT_INFO))


def version_user_graph(db_session, endpoint_id, form):
    """
    :param db_session: session for the database
    :param endpoint_id: the endpoint_id to filter the data on
    :param form: form for reducing the size of the graph
    :return: an HTML bubble plot
    """
    users = get_users(db_session, endpoint_id, form.get_slider_value(0))
    versions = get_versions(db_session, endpoint_id, form.get_slider_value(1))

    first_request = get_first_requests(db_session, endpoint_id)
    values = get_two_columns_grouped(db_session, Request.group_by, Request.endpoint_id == endpoint_id)
    data = [[get_value(values, (user, v)) for v in versions] for user in users]

    average = get_average_bubble_size(data)
    trace = [scatter(
        x=[format_version(v, get_value(first_request, v)) for v in versions],
        hovertext=['Time: {:,.1f}ms'.format(data[i][j]) for j in range(len(versions))],
        y=[users[i]] * len(versions),
        name=users[i],
        mode='markers',
        marker={
            'color': [get_color(users[i])] * len(versions),
            'size': [math.sqrt(d) for d in data[i]],
            'sizeref': average,
            'sizemode': 'area'
        }
    ) for i in range(len(users))]

    layout = get_layout(
        height=350 + 40 * len(trace),
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'title': 'Users', 'type': 'category', 'autorange': 'reversed'},
        margin=get_margin(b=200)
    )
    return get_figure(layout, trace)
