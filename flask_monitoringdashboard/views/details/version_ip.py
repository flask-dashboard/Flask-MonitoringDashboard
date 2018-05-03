import math

from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_average_bubble_size, scatter, get_layout, get_margin, get_figure
from flask_monitoringdashboard.core.utils import get_endpoint_details, formatter
from flask_monitoringdashboard.database import FunctionCall, session_scope
from flask_monitoringdashboard.database.count import count_ip
from flask_monitoringdashboard.database.endpoint import get_ip_sorted
from flask_monitoringdashboard.database.function_calls import get_median
from flask_monitoringdashboard.database.versions import get_date_first_request, get_versions


@blueprint.route('/result/<end>/time_per_version_per_ip', methods=['GET', 'POST'])
@secure
def result_time_per_version_per_ip(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        form = get_slider_form(count_ip(db_session, end))
    graph = get_time_per_version_per_ip(end, form)
    return render_template('fmd_dashboard/graph-details.html', details=details, graph=graph, form=form)


def get_time_per_version_per_ip(end, form):
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
        title='Median execution time for every user per version',
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin(b=200)
    )
    return get_figure(layout, trace)
