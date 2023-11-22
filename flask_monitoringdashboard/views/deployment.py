import datetime

from flask import jsonify

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard.core.utils import get_details
from flask_monitoringdashboard.database import session_scope



@blueprint.route('/api/deploy_details')
@secure
def deploy_details():
    """
    :return: A JSON-object with deployment details
    """
    post_to_back_if_telemetry_enabled(**{'name': 'deploy_details'})

    with session_scope() as session:
        details = get_details(session)
    details['first-request'] = to_local_datetime(
        datetime.datetime.fromtimestamp(details['first-request'])
    )
    details['first-request-version'] = to_local_datetime(
        datetime.datetime.fromtimestamp(details['first-request-version'])
    )
    return jsonify(details)


@blueprint.route('/api/deploy_config')
@secure
def deploy_config():
    """
    :return: A JSON-object with configuration details
    """
    post_to_back_if_telemetry_enabled(**{'name': 'deploy_config'})
    return jsonify(
        {
            'database_name': config.database_name,
            'outlier_detection_constant': config.outlier_detection_constant,
            'timezone': str(config.timezone),
            'colors': config.colors,
        }
    )
