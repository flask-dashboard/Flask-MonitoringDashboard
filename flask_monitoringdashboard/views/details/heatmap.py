from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.views.dashboard.heatmap import get_heatmap
from flask_monitoringdashboard.core.utils import get_endpoint_details


@blueprint.route('/result/<end>/heatmap', methods=['GET', 'POST'])
@secure
def result_heatmap(end):
    form = get_daterange_form()
    return render_template('dashboard/graph-details.html', form=form, details=get_endpoint_details(end),
                           graph=get_heatmap(form, end))
