from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database import Outlier
from flask_monitoringdashboard.database.outlier import get_outliers_sorted
from flask_monitoringdashboard.core.auth import secure
from .utils import get_endpoint_details


@blueprint.route('/result/<end>/outliers')
@secure
def result_outliers(end):
    table = get_outliers_sorted(end, Outlier.execution_time)
    return render_template('endpoint/outliers.html', details=get_endpoint_details(end), table=table)
