from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.views.dashboard.heatmap import get_heatmap
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/heatmap')
@secure
def result_heatmap(end):
    return render_template('endpoint/plotly.html', details=get_endpoint_details(end), graph=get_heatmap(end))
