from flask import jsonify

from flask_monitoringdashboard.controllers.outliers import get_outlier_graph, get_outlier_table
from flask_monitoringdashboard.database.count import count_outliers

from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard import blueprint


@blueprint.route('/api/num_outliers/<int:endpoint_id>')
@secure
def num_outliers(endpoint_id):
    post_to_back_if_telemetry_enabled(**{'name': f'num_outliers/{endpoint_id}'})
    with session_scope() as session:
        return jsonify(count_outliers(session, endpoint_id))


@blueprint.route('/api/outlier_graph/<int:endpoint_id>')
@secure
def outlier_graph(endpoint_id):
    post_to_back_if_telemetry_enabled(**{'name': f'outlier_graph/{endpoint_id}'})
    with session_scope() as session:
        return jsonify(get_outlier_graph(session, endpoint_id))


@blueprint.route('/api/outlier_table/<int:endpoint_id>/<offset>/<per_page>')
@secure
def outlier_table(endpoint_id, offset, per_page):
    post_to_back_if_telemetry_enabled(**{'name': f'outlier_table/{endpoint_id}'})
    with session_scope() as session:
        return jsonify(get_outlier_table(session, endpoint_id, offset, per_page))
