from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.endpoint import get_all_measurement_per_column, get_group_by_sorted
from flask_monitoringdashboard.database.count import count_users
from flask_monitoringdashboard.core.utils import get_endpoint_details


@blueprint.route('/result/<end>/time_per_user', methods=['GET', 'POST'])
@secure
def result_time_per_user(end):
    form = get_slider_form(count_users(end))
    graph = get_time_per_user(end, form)

    return render_template('dashboard/graph-details.html', details=get_endpoint_details(end), graph=graph, form=form)


def get_time_per_user(end, form):
    """
    Return an HTML box plot with a specific number of
    :param end: get the data for this endpoint only
    :param form: instance of SliderForm
    :return:
    """
    data = []
    for group_by in get_group_by_sorted(end, form.get_slider_value()):
        values = [str(c.execution_time) for c in
                  get_all_measurement_per_column(endpoint=end, column=FunctionCall.group_by, value=group_by)]
        data.append(boxplot(values, name=str(group_by)))

    layout = get_layout(
        height=350 + 40 * len(data),
        title='Execution time for every user for endpoint: ' + end,
        xaxis={'title': 'Execution time (ms)'},
        yaxis={'type': 'category', 'title': 'User'}
    )
    return get_figure(layout, data)
