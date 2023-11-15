from flask import jsonify, request, json
from sqlalchemy.exc import SQLAlchemyError
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard import blueprint, telemetry_config
from flask_monitoringdashboard.core.telemetry import get_telemetry_user
from flask_monitoringdashboard.database import session_scope


@blueprint.route('/api/telemetry/accept_telemetry_consent', methods=['GET', 'POST'])
def accept_telemetry_consent():
    with session_scope() as session:
        try:
            print('TELEMETRY CONSENT')
            telemetry_user = get_telemetry_user(session)
            data = request.get_json()

            if 'consent' in data and isinstance(data['consent'], bool) and data['consent']:  # if True then agreed
                telemetry_user.monitoring_consent = 3  # agree to monitoring
                telemetry_config.telemetry_consent = True

            else:
                telemetry_user.monitoring_consent = 2  # reject monitoring

            session.commit()

        except SQLAlchemyError as e:
            print('error committing telemetry consent to database', e)
            session.rollback()

        # Return no content
        return '', 204


@blueprint.route('/api/telemetry/survey_has_been_filled', methods=['POST'])
def survey_has_been_filled():
    with session_scope() as session:
        try:
            telemetry_user = get_telemetry_user(session)
            telemetry_user.survey_filled = True
            session.commit()

        except SQLAlchemyError as e:
            print('error committing survey consent to database', e)
            session.rollback()

    # Return no content
    return '', 204


@blueprint.route('/api/telemetry/get_is_telemetry_answered', methods=['GET', 'POST'])
@secure
def get_is_telemetry_answered():
    with session_scope() as session:
        print('IS TELEMETRY ANSWERED')
        telemetry_user = get_telemetry_user(session)
        res = True if telemetry_user.monitoring_consent in (2, 3) else False
        return {'is_telemetry_answered': res}


@blueprint.route('/api/telemetry/get_is_survey_filled', methods=['POST'])
def get_is_survey_filled():
    with session_scope() as session:
        telemetry_user = get_telemetry_user(session)
        res = True if telemetry_user.survey_filled in (2, 3) else False
        return {'is_survey_filled': res}
