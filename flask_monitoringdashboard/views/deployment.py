import datetime

from flask import jsonify

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.core.utils import get_details
from flask_monitoringdashboard.database import session_scope


@blueprint.route('/api/deploy_details')
@secure
def deploy_details():
    """
    :return: A JSON-object with deployment details
    """
    with session_scope() as db_session:
        details = get_details(db_session)
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
    return jsonify(
        {
            'database_name': config.database_name,
            'username': config.username,
            'guest_username': config.guest_username,
            'outlier_detection_constant': config.outlier_detection_constant,
            'timezone': str(config.timezone),
            'colors': config.colors,
        }
    )
