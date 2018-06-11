from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot
from flask_monitoringdashboard.core.info_box import get_plot_info
from flask_monitoringdashboard.core.utils import get_endpoint_details, simplify
from flask_monitoringdashboard.database import Request, session_scope
from flask_monitoringdashboard.database.count import count_users
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.data_grouped import get_user_data_grouped
from flask_monitoringdashboard.database.endpoint import get_users

TITLE = 'Per-User Performance'

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents (a subset of) 
all unique users.'''

CONTENT_INFO = '''This graph shows a horizontal boxplot for the unique users that uses the application.
With this graph you can found out whether the performance is different across different users.'''


@blueprint.route('/endpoint/<endpoint_id>/users', methods=['GET', 'POST'])
@secure
def users(endpoint_id):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, endpoint_id)
        form = get_slider_form(count_users(db_session, endpoint_id), title='Select the number of users')
    graph = users_graph(endpoint_id, form)

    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph, form=form,
                           title='{} for {}'.format(TITLE, details['endpoint']),
                           information=get_plot_info(AXES_INFO, CONTENT_INFO))


def users_graph(id, form):
    """
    Return an HTML box plot with a specific number of
    :param id: get the data for this endpoint only
    :param form: instance of SliderForm
    :return:
    """
    with session_scope() as db_session:
        users = get_users(db_session, id, form.get_slider_value())
        times = get_user_data_grouped(db_session, lambda x: simplify(x, 10), Request.endpoint_id == id)
        data = [boxplot(name=u, values=get_value(times, u)) for u in users]

    layout = get_layout(
        height=350 + 40 * len(data),
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'User'}
    )
    return get_figure(layout, data)
