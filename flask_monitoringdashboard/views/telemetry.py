from flask import jsonify, request, json
from sqlalchemy.exc import SQLAlchemyError
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard import blueprint, telemetry_config
from flask_monitoringdashboard.core.config import TelemetryConfig
from flask_monitoringdashboard.core.telemetry import get_telemetry_user
from flask_monitoringdashboard.database import session_scope


@blueprint.route('/telemetry/accept_telemetry_consent', methods=['POST'])
def accept_telemetry_consent():
    with session_scope() as session:
        try:
            telemetry_user = get_telemetry_user(session)
            data = request.get_json()
            if 'consent' in data and isinstance(data['consent'], bool) and data.get('consent'):  # if True then agreed
                telemetry_user.monitoring_consent = TelemetryConfig.ACCEPTED  # agree to monitoring
                telemetry_config.telemetry_consent = True
            else:
                telemetry_user.monitoring_consent = TelemetryConfig.REJECTED  # reject monitoring
                telemetry_config.telemetry_consent = False
            session.commit()

        except SQLAlchemyError as e:
            print('error committing telemetry consent to database', e)
            session.rollback()

    # Return no content
    return '', 204


@blueprint.route('/telemetry/survey_has_been_filled', methods=['GET'])
def survey_has_been_filled():
    with session_scope() as session:
        try:
            telemetry_user = get_telemetry_user(session)
            telemetry_user.survey_filled = TelemetryConfig.ACCEPTED
            session.commit()

        except SQLAlchemyError as e:
            print('error committing survey consent to database', e)
            session.rollback()

    # Return no content
    return '', 204


@blueprint.route('/telemetry/get_is_telemetry_answered', methods=['GET'])
def get_is_telemetry_answered():
    with session_scope() as session:
        telemetry_user = get_telemetry_user(session)
        res = True if telemetry_user.monitoring_consent in (TelemetryConfig.REJECTED, TelemetryConfig.ACCEPTED) else False
        return {'is_telemetry_answered': res}


@blueprint.route('/telemetry/get_is_survey_filled', methods=['GET'])
def get_is_survey_filled():
    with session_scope() as session:
        telemetry_user = get_telemetry_user(session)
        res = True if telemetry_user.survey_filled in (TelemetryConfig.REJECTED, TelemetryConfig.ACCEPTED) else False
        return {'is_survey_filled': res}
