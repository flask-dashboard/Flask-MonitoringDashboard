import plotly
import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form, get_days
from flask_monitoringdashboard.database.function_calls import get_requests_per_day, get_endpoints


@blueprint.route('/measurements/requests', methods=['GET', 'POST'])
@secure
def page_number_of_requests_per_endpoint():
    form = get_daterange_form(numdays=10)
    return render_template('dashboard/graph.html', form=form, graph=get_stacked_bar(form),
                           title='Requests per endpoint')


def get_stacked_bar(form):
    """
    Returns a horizontal boxplot with the number of requests per day.
    :param form: must be the form that is obtained by get_daterange_form
    :return:
    """
    days = get_days(form)

    # create graph
    trace = []
    for endpoint in get_endpoints():
        trace.append(go.Bar(
            y=days,
            x=get_requests_per_day(endpoint, days),
            name=endpoint,
            orientation='h',
            marker={'color': get_color(endpoint)}
        ))

    layout = go.Layout(
        barmode='stack',
        autosize=True,
        height=350 + 40 * len(days),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=True,
        title='Number of requests per endpoint per day',
        xaxis={'title': 'Number of requests'},
        yaxis={'autorange': 'reversed'}
    )

    return plotly.offline.plot(go.Figure(data=trace, layout=layout), output_type='div', show_link=False)
