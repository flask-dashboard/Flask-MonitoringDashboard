from flask import jsonify, request, json
from sqlalchemy.exc import SQLAlchemyError

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.utils import get_telemetry_user
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.database import session_scope


@blueprint.route('/api/telemetry/accept_telemetry', methods=['POST'])
@secure
def accept_telemetry():
    with session_scope() as session:
        try:
            data = request.json
            telemetry_user = get_telemetry_user(session)
            if data.consent:
                telemetry_user.monitoring_consent = 3  # agree to monitoring
                config.telemetry_consent = True
            else:
                telemetry_user.monitoring_consent = 2  # reject monitoring
            session.commit()
        except SQLAlchemyError as e:
            print('error committing telemetry consent to database', e)
            session.rollback()

    return True


@blueprint.route('/api/telemetry/survey_filled', methods=['POST'])
@secure
def survey_filled():
    with session_scope() as session:
        try:
            telemetry_user = get_telemetry_user(session)
            telemetry_user.survey_filled = True
            session.commit()
        except SQLAlchemyError as e:
            print('error committing survey consent to database', e)
            session.rollback()

    return True


@blueprint.route('/api/telemetry/get_telemetry_answered', methods=['POST'])
@secure
def get_telemetry_answered():
    with session_scope() as session:
        telemetry_user = get_telemetry_user(session)
        if telemetry_user.monitoring_consent == 3:
            return True
        return False


@blueprint.route('/api/telemetry/get_survey_filled', methods=['POST'])
@secure
def get_survey_filled():
    with session_scope() as session:
        telemetry_user = get_telemetry_user(session)
        if telemetry_user.survey_filled:
            return True
        return False
