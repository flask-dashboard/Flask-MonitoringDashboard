from flask import jsonify

from flask_monitoringdashboard.controllers.outliers import get_outlier_graph, get_outlier_table
from flask_monitoringdashboard.database.count import count_outliers

from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard import blueprint


@blueprint.route('/api/num_outliers/<endpoint_id>')
@secure
def num_outliers(endpoint_id):
    with session_scope() as db_session:
        return jsonify(count_outliers(db_session, endpoint_id))


@blueprint.route('/api/outlier_graph/<endpoint_id>')
@secure
def outlier_graph(endpoint_id):
    with session_scope() as db_session:
        return jsonify(get_outlier_graph(db_session, endpoint_id))


@blueprint.route('/api/outlier_table/<endpoint_id>/<offset>/<per_page>')
@secure
def outlier_table(endpoint_id, offset, per_page):
    with session_scope() as db_session:
        return jsonify(get_outlier_table(db_session, endpoint_id, offset, per_page))
