from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.views.dashboard.heatmap import hourly_load_graph, TITLE, AXES_INFO
from flask_monitoringdashboard.core.utils import get_endpoint_details


CONTENT_INFO = '''The color of the cell presents the number of requests that the application received 
in a single hour. The darker the cell, the more requests it has processed. This information can be used 
to validate on which moment of the day this endpoint processes to most requests.'''


@blueprint.route('/endpoint/<end>/hourly_load', methods=['GET', 'POST'])
@secure
def endpoint_hourly_load(end):
    form = get_daterange_form()
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
    return render_template('fmd_dashboard/graph-details.html', form=form, details=details,
                           graph=hourly_load_graph(form, end), title='{} for {}'.format(TITLE, end),
                           information=get_information(AXES_INFO, CONTENT_INFO))
