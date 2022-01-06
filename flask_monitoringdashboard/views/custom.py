import datetime

from flask.json import jsonify

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.custom_graph import get_custom_graphs
from flask_monitoringdashboard.database.custom_graph import get_graph_data


@blueprint.route('/api/custom_graphs')
@secure
def custom_graphs():
    graphs = get_custom_graphs()
    if not graphs:
        return jsonify([])
    return jsonify(graphs)


@blueprint.route('/api/custom_graph/<graph_id>/<start_date>/<end_date>')
@secure
def custom_graph(graph_id, start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    return jsonify(get_graph_data(graph_id, start_date, end_date))
