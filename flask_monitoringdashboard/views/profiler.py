from flask import jsonify

from flask_monitoringdashboard.controllers.profiler import get_profiler_table, get_grouped_profiler
from flask_monitoringdashboard.database import session_scope, Endpoint

from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database.count import count_profiled_requests


@blueprint.route('/api/num_profiled/<int:endpoint_id>')
@secure
def num_profiled(endpoint_id):
    post_to_back_if_telemetry_enabled(**{'name': f'num_profiled/{endpoint_id}'})
    with session_scope() as session:
        return jsonify(count_profiled_requests(session, endpoint_id))


@blueprint.route('/api/profiler_table/<int:endpoint_id>/<offset>/<per_page>')
@secure
def profiler_table(endpoint_id, offset, per_page):
    post_to_back_if_telemetry_enabled(**{'name': f'profiled_table/{endpoint_id}'})
    with session_scope() as session:
        return jsonify(get_profiler_table(session, endpoint_id, offset, per_page))


@blueprint.route('/api/grouped_profiler/<int:endpoint_id>')
@secure
def grouped_profiler(endpoint_id):
    post_to_back_if_telemetry_enabled(**{'name': f'grouped_profiler/{endpoint_id}'})
    with session_scope() as session:
        return jsonify(get_grouped_profiler(session, endpoint_id))
