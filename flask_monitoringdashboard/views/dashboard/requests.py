from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.core.plot import barplot, get_figure, get_layout
from flask_monitoringdashboard.database.function_calls import get_requests_per_day, get_endpoints

TITLE = 'Requests per endpoint per day'


@blueprint.route('/measurements/requests', methods=['GET', 'POST'])
@secure
def page_number_of_requests_per_endpoint():
    form = get_daterange_form(num_days=10)
    return render_template('dashboard/graph.html', form=form, graph=get_stacked_bar(form), title=TITLE)


def get_stacked_bar(form):
    """
    Returns a horizontal boxplot with the number of requests per day.
    :param form: must be the form that is obtained by get_daterange_form
    :return:
    """
    days = form.get_days()
    data = [barplot(x=get_requests_per_day(end, days), y=days, name=end) for end in get_endpoints()]

    layout = get_layout(
        barmode='stack',
        height=350 + 40 * len(days),
        showlegend=True,
        title=TITLE,
        xaxis={'title': 'Number of requests'},
        yaxis={'type': 'category', 'autorange': 'reversed'}
    )

    return get_figure(layout=layout, data=data)
