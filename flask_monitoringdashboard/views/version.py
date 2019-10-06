from flask import jsonify, request, json

from flask_monitoringdashboard.controllers.versions import (
    get_multi_version_data,
    get_version_user_data,
    get_version_ip_data,
)
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database.versions import get_versions


@blueprint.route('/api/versions')
@blueprint.route('/api/versions/<endpoint_id>')
@secure
def versions(endpoint_id=None):
    """
    :param endpoint_id: integer
    :return: A JSON-list with all versions of a specific endpoint (version represented by a string)
    """
    with session_scope() as db_session:
        version_dates = get_versions(db_session, endpoint_id)
        dicts = []
        for vt in version_dates:
            dicts.append({'version': vt[0], 'date': vt[1]})
        return jsonify(dicts)


@blueprint.route('/api/multi_version', methods=['POST'])
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


@blueprint.route('/api/version_user/<endpoint_id>', methods=['POST'])
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


@blueprint.route('/api/version_ip/<endpoint_id>', methods=['POST'])
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
