from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.views.dashboard.heatmap import get_heatmap
from flask_monitoringdashboard.core.utils import get_endpoint_details


@blueprint.route('/result/<end>/heatmap', methods=['GET', 'POST'])
@secure
def result_heatmap(end):
    form = get_daterange_form()
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
    return render_template('fmd_dashboard/graph-details.html', form=form, details=details, graph=get_heatmap(form, end))
