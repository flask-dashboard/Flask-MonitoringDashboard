from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column, \
    get_endpoint_column_user_sorted
from flask_monitoringdashboard.database.count import count_users
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/time_per_user', methods=['GET', 'POST'])
@secure
def result_time_per_user(end):
    form = get_slider_form(count_users(end))
    graph = get_time_per_user(end, form)

    return render_template('endpoint/time_per_user.html', details=get_endpoint_details(end), graph=graph, form=form)


def get_time_per_user(end, form):
    """
    Return an HTML box plot with a specific number of
    :param end: get the data for this endpoint only
    :param form: instance of SliderForm
    :return:
    """
    users = [str(c.group_by) for c in get_endpoint_column_user_sorted(endpoint=end, column=FunctionCall.group_by,
                                                                      limit=form.get_slider_value())]
    data = []
    for user in users:
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.group_by, value=user)]
        data.append(boxplot(values, name=user))
    data.reverse()
    layout = get_layout(
        height=350 + 40 * len(data),
        title='Execution time for every user for endpoint: ' + end,
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'title': 'User'}
    )
    return get_figure(layout, data)
