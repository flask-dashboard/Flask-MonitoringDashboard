from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.core.plot import barplot, get_figure, get_layout
from flask_monitoringdashboard.core.info_box import get_plot_info
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count_group import count_requests_per_day, get_value
from flask_monitoringdashboard.database.endpoint import get_endpoints

TITLE = 'Daily API Utilization'

AXES_INFO = '''The X-axis presents the amount of requests. The Y-axis presents a number 
of days'''

CONTENT_INFO = '''This graph presents a horizontal stacked barplot. Each endpoint is represented by a 
color. In the legend on the right, you can disable a certain endpoint by clicking on it. You can also
show in the information of a single endpoint by double clicking that endpoint in the legend. The 
information from this graph can be used to see on which days (a subset of) the endpoints are used to 
most.'''


@blueprint.route('/requests', methods=['GET', 'POST'])
@secure
def requests():
    form = get_daterange_form(num_days=10)
    return render_template('fmd_dashboard/graph.html', form=form, graph=requests_graph(form), title=TITLE,
                           information=get_plot_info(AXES_INFO, CONTENT_INFO))


def requests_graph(form):
    """
    Returns a horizontal box plot with the number of requests per day.
    :param form: must be the form that is obtained by get_daterange_form
    :return:
    """
    days = form.get_days()
    with session_scope() as db_session:
        hits = count_requests_per_day(db_session, days)
        data = [barplot(x=[get_value(hits_day, end.id) for hits_day in hits], y=days, name=end.name)
                for end in get_endpoints(db_session)]
    layout = get_layout(
        barmode='stack',
        height=350 + 40 * len(days),
        showlegend=True,
        xaxis={'title': 'Number of requests'},
        yaxis={'type': 'category'}
    )

    return get_figure(layout=layout, data=data)
