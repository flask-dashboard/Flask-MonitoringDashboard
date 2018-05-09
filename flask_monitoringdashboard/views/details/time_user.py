from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count import count_users
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column, get_group_by_sorted


TITLE = 'Per-User Performance'

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents (a subset of) 
all unique users.'''

CONTENT_INFO = '''This graph shows a horizontal boxplot for the unique users that uses the application.
With this graph you can found out whether the performance is different across different users.'''


@blueprint.route('/endpoint/<end>/users', methods=['GET', 'POST'])
@secure
def users(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        form = get_slider_form(count_users(db_session, end))
    graph = users_graph(end, form)

    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph, form=form,
                           title='{} for {}'.format(TITLE, end), information=
                           get_information(AXES_INFO, CONTENT_INFO))


def users_graph(end, form):
    """
    Return an HTML box plot with a specific number of
    :param end: get the data for this endpoint only
    :param form: instance of SliderForm
    :return:
    """
    data = []
    with session_scope() as db_session:
        for group_by in get_group_by_sorted(db_session, end, form.get_slider_value()):
            values = [str(c.execution_time) for c in
                      get_all_measurement_per_column(db_session, endpoint=end, column=FunctionCall.group_by,
                                                     value=group_by)]
            data.append(boxplot(values, name=str(group_by)))

    layout = get_layout(
        height=350 + 40 * len(data),
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'User'}
    )
    return get_figure(layout, data)
