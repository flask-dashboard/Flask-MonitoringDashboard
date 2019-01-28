import datetime

from flask import jsonify, request, json

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.controllers.endpoints import get_endpoint_overview, get_endpoint_users, \
    get_endpoint_versions, get_api_performance, set_endpoint_rule
from flask_monitoringdashboard.controllers.outliers import get_outlier_graph, get_outlier_table
from flask_monitoringdashboard.controllers.requests import get_num_requests_data, get_hourly_load
from flask_monitoringdashboard.controllers.versions import get_version_user_data, get_version_ip_data, \
    get_multi_version_data
from flask_monitoringdashboard.controllers.profiler import get_profiler_table, get_grouped_profiler
from flask_monitoringdashboard.core.auth import secure, admin_secure
from flask_monitoringdashboard.core.custom_graph import get_custom_graphs
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.core.utils import get_details, get_endpoint_details
from flask_monitoringdashboard.database import session_scope, row2dict
from flask_monitoringdashboard.database.count import count_outliers, count_profiled_requests
from flask_monitoringdashboard.database.custom_graph import get_graph_data
from flask_monitoringdashboard.database.endpoint import get_endpoints, get_users, get_ips
from flask_monitoringdashboard.database.versions import get_versions


@blueprint.route('/api/overview')
@secure
def get_overview():
    """
    Get information per endpoint about the number of hits and median execution time
    :return: A JSON-list with a JSON-object per endpoint
    """
    with session_scope() as db_session:
        return jsonify(get_endpoint_overview(db_session))


@blueprint.route('/api/versions')
@blueprint.route('api/versions/<endpoint_id>')
@secure
def versions(endpoint_id=None):
    """
    :param endpoint_id: integer
    :return: A JSON-list with all versions of a specific endpoint (version represented by a string)
    """
    with session_scope() as db_session:
        return jsonify(get_versions(db_session, endpoint_id))


@blueprint.route('/api/users/<endpoint_id>')
@secure
def users(endpoint_id):
    """
    :param endpoint_id: integer
    :return: A JSON-list with all users of a specific endpoint (user represented by a string)
    """
    with session_scope() as db_session:
        return jsonify(get_users(db_session, endpoint_id))


@blueprint.route('/api/ip/<endpoint_id>')
@secure
def ips(endpoint_id):
    """
    :param endpoint_id: integer
    :return: A JSON-list with all IP-addresses of a specific endpoint (ip represented by a string)
    """
    with session_scope() as db_session:
        return jsonify(get_ips(db_session, endpoint_id))


@blueprint.route('/api/endpoints')
@secure
def endpoints():
    """
    :return: A JSON-list with information about every endpoint (encoded in a JSON-object)
        For more information per endpoint, see :func: get_overview
    """
    with session_scope() as db_session:
        return jsonify([row2dict(row) for row in get_endpoints(db_session)])


@blueprint.route('api/multi_version', methods=['POST'])
@secure
def multi_version():
    """
        input must be a JSON-object, with a list of endpoints and versions, such as:
          {
            endpoints: ['endpoint0', endpoint1],
            versions: ['0.1', '0.2', '0.3']
          }
    :return: A JSON-list for all endpoints, with a JSON-list for every version.
        output: {
            [
              [10, 11, 12],
              [13, 14, 15]
            ]
          }
    """
    data = json.loads(request.data)['data']
    endpoints = data['endpoints']
    versions = data['versions']

    with session_scope() as db_session:
        return jsonify(get_multi_version_data(db_session, endpoints, versions))


@blueprint.route('api/version_user/<endpoint_id>', methods=['POST'])
@secure
def version_user(endpoint_id):
    """
        input must be a JSON-object, with a list of versions and users, such as:
          {
            users: ['user0', user1],
            versions: ['0.1', '0.2', '0.3']
          }
    :return: A JSON-list for all users, with a JSON-list for every version.
        output: {
            data: [
              [10, 11, 12],
              [13, 14, 15]
            ],
            versions: [
              { date: '...', version: '0.1'},
              { date: '...', version: '0.2'},
              { date: '...', version: '0.3'}
            ]
          }
    """
    data = json.loads(request.data)['data']
    versions = data['versions']
    users = data['users']

    with session_scope() as db_session:
        return jsonify(get_version_user_data(db_session, endpoint_id, versions, users))


@blueprint.route('api/version_ip/<endpoint_id>', methods=['POST'])
@secure
def version_ip(endpoint_id):
    """
        input must be a JSON-object, with a list of versions and IP-addresses, such as:
          {
            ip: ['127.0.0.1', '127.0.0.2'],
            versions: ['0.1', '0.2', '0.3']
          }
    :return: A JSON-list for all IP-addresses, with a JSON-list for every version.
        output: {
            data: [
              [10, 11, 12],
              [13, 14, 15]
            ],
            versions: [
              { date: '...', version: '0.1'},
              { date: '...', version: '0.2'},
              { date: '...', version: '0.3'}
            ]
          }
    """
    data = json.loads(request.data)['data']
    versions = data['versions']
    ips = data['ip']

    with session_scope() as db_session:
        return jsonify(get_version_ip_data(db_session, endpoint_id, versions, ips))


@blueprint.route('/api/requests/<start_date>/<end_date>')
@secure
def num_requests(start_date, end_date):
    """
    :param start_date: must be in the following form: yyyy-mm-dd
    :param end_date: must be in the following form: yyyy-mm-dd
    :return: A JSON-list with the following object: {
          'name': 'endpoint',
          'values': [list with an integer per day],
        }
    """
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    with session_scope() as db_session:
        return jsonify(get_num_requests_data(db_session, start_date, end_date))


@blueprint.route('/api/api_performance', methods=['POST'])
@secure
def api_performance():
    """
    input must be a JSON-object, with the following value: {
          'data': {
            'endpoint': ['endpoint', 'endpoint2']
          }
        }
    :return: A JSON-list for every endpoint with the following JSON-object: {
          'name': 'endpoint',
          'values': [100, 101, 102, ...]
        }
    """
    data = json.loads(request.data)['data']
    endpoints = data['endpoints']

    with session_scope() as db_session:
        return jsonify(get_api_performance(db_session, endpoints))


@blueprint.route('/api/set_rule', methods=['POST'])
@admin_secure
def set_rule():
    """
        The data from the form is validated and processed, such that the required rule is monitored
    """
    endpoint_name = request.form['name']
    value = int(request.form['value'])
    with session_scope() as db_session:
        set_endpoint_rule(db_session, endpoint_name, value)
    return 'OK'


@blueprint.route('api/deploy_details')
@secure
def deploy_details():
    """
    :return: A JSON-object with deployment details
    """
    with session_scope() as db_session:
        details = get_details(db_session)
    details['first-request'] = to_local_datetime(datetime.datetime.fromtimestamp(details['first-request']))
    details['first-request-version'] = to_local_datetime(datetime.datetime.
                                                         fromtimestamp(details['first-request-version']))
    return jsonify(details)


@blueprint.route('api/deploy_config')
@secure
def deploy_config():
    """
    :return: A JSON-object with configuration details
    """
    return jsonify({
        'database_name': config.database_name,
        'username': config.username,
        'guest_username': config.guest_username,
        'outlier_detection_constant': config.outlier_detection_constant,
        'timezone': str(config.timezone),
        'colors': config.colors
    })


@blueprint.route('api/endpoint_info/<endpoint_id>')
@secure
def endpoint_info(endpoint_id):
    """
    :return: A JSON-object with endpoint details, such as:
        - color: hashed color of the endpoint,
        - endpoint: endpoint-name
        - id: endpoint id
        - methods: HTTP methods (encoded as a JSON-list)
        - monitor-level: monitor level for this endpoint
        - rules: all rules for this endpoint (encoded as a JSON-list)
        - total_hits: number of hits
        - url: link to this endpoint
    """
    with session_scope() as db_session:
        return jsonify(get_endpoint_details(db_session, endpoint_id))


@blueprint.route('api/hourly_load/<start_date>/<end_date>')
@blueprint.route('api/hourly_load/<start_date>/<end_date>/<endpoint_id>')
@secure
# both days must be in the form: yyyy-mm-dd
def hourly_load(start_date, end_date, endpoint_id=None):
    """
    :param start_date: must be in the following form: yyyy-mm-dd
    :param end_date: must be in the following form: yyyy-mm-dd
    :param endpoint_id: if specified, filter on this endpoint
    :return: A JSON-object: {
          'data': [ [hits for 0:00-1:00 per day], [hits for 1:00-2:00 per day], ...]
          'days': ['start_date', 'start_date+1', ..., 'end_date'],
        }
    """
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    with session_scope() as db_session:
        return jsonify(get_hourly_load(db_session, endpoint_id, start_date, end_date))


@blueprint.route('api/endpoint_versions/<endpoint_id>', methods=['POST'])
@secure
def endpoint_versions(endpoint_id):
    with session_scope() as db_session:
        data = json.loads(request.data)['data']
        versions = data['versions']
        return jsonify(get_endpoint_versions(db_session, endpoint_id, versions))


@blueprint.route('api/endpoint_users/<endpoint_id>', methods=['POST'])
@secure
def endpoint_users(endpoint_id):
    with session_scope() as db_session:
        data = json.loads(request.data)['data']
        users = data['users']
        return jsonify(get_endpoint_users(db_session, endpoint_id, users))


@blueprint.route('api/num_outliers/<endpoint_id>')
@secure
def num_outliers(endpoint_id):
    with session_scope() as db_session:
        return jsonify(count_outliers(db_session, endpoint_id))


@blueprint.route('api/outlier_graph/<endpoint_id>')
@secure
def outlier_graph(endpoint_id):
    with session_scope() as db_session:
        return jsonify(get_outlier_graph(db_session, endpoint_id))


@blueprint.route('api/outlier_table/<endpoint_id>/<offset>/<per_page>')
@secure
def outlier_table(endpoint_id, offset, per_page):
    with session_scope() as db_session:
        return jsonify(get_outlier_table(db_session, endpoint_id, offset, per_page))


@blueprint.route('api/num_profiled/<endpoint_id>')
@secure
def num_profiled(endpoint_id):
    with session_scope() as db_session:
        return jsonify(count_profiled_requests(db_session, endpoint_id))


@blueprint.route('api/profiler_table/<endpoint_id>/<offset>/<per_page>')
@secure
def profiler_table(endpoint_id, offset, per_page):
    with session_scope() as db_session:
        return jsonify(get_profiler_table(db_session, endpoint_id, offset, per_page))


@blueprint.route('/api/grouped_profiler/<endpoint_id>')
@secure
def grouped_profiler(endpoint_id):
    with session_scope() as db_session:
        return jsonify(get_grouped_profiler(db_session, endpoint_id))


@blueprint.route('/api/custom_graphs')
@secure
def custom_graphs():
    return jsonify([row2dict(row) for row in get_custom_graphs()])


@blueprint.route('/api/custom_graph/<graph_id>/<start_date>/<end_date>')
@secure
def custom_graph(graph_id, start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    with session_scope() as db_session:
        return jsonify(get_graph_data(db_session, graph_id, start_date, end_date))
