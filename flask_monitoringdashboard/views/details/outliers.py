from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database import Outlier
from flask_monitoringdashboard.database.outlier import get_outliers_sorted
from flask_monitoringdashboard.auth import secure
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/outliers')
@secure
def result_outliers(end):
    title = 'Outliers for endpoint: {}'.format(end)
    table = get_outliers_sorted(end, Outlier.execution_time)
    return render_template('endpoint/outliers.html', title=title, details=get_endpoint_details(end), table=table)
