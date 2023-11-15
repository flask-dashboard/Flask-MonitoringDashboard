import datetime
import requests

from sqlalchemy.exc import NoResultFound, MultipleResultsFound, SQLAlchemyError

from flask_monitoringdashboard import telemetry_config
from flask_monitoringdashboard.core.blueprints import get_blueprint
from flask_monitoringdashboard.database import TelemetryUser, Endpoint


def get_telemetry_user(session):
    try:
        return session.query(TelemetryUser).one()

    except (MultipleResultsFound, NoResultFound):
        session.query(TelemetryUser).delete()
        initialize_telemetry_session(session)
        get_telemetry_user(session)

    except SQLAlchemyError as e:
        session.rollback()
        initialize_telemetry_session(session)
        get_telemetry_user(session)


def initialize_telemetry_session(session):
    """
    Initializes the monitoring session by creating or updating an entry
    """
    try:
        # check if user is registered
        if not bool(session.query(TelemetryUser).all()):
            telemetry_user = TelemetryUser()
            session.add(telemetry_user)
            session.commit()
        else:
            telemetry_user = session.query(TelemetryUser).one()
            telemetry_user.times_accessed += 1
            telemetry_user.last_accessed = datetime.datetime.utcnow()
            session.commit()

        # check if telemetry's been agreed on
        telemetry_config.telemetry_consent = True if telemetry_user.monitoring_consent == 3 else False

        # save the telemetry_config for quick access
        telemetry_config.fmd_user = telemetry_user.id
        telemetry_config.telemetry_initialized = True
        telemetry_config.telemetry_session = telemetry_user.times_accessed

        # collect user data
        endpoints = session.query(Endpoint.name).all()
        blueprints = set(get_blueprint(endpoint) for endpoint, in endpoints)
        no_of_endpoints = len(endpoints)
        no_of_blueprints = len(blueprints)

        data = {'endpoints': no_of_endpoints,
                'blueprints': no_of_blueprints,
                'time_accessed': telemetry_user.last_accessed.strftime('%Y-%m-%d %H:%M:%S')
                }

        # post user data
        post_to_back('UserSession', **data)

    except (MultipleResultsFound, NoResultFound) as e:
        print(e)
        session.query(TelemetryUser).delete()
        initialize_telemetry_session(session)

    except SQLAlchemyError as e:
        print(e)
        session.rollback()


def post_to_back(class_name='Endpoints', **kwargs):
    if telemetry_config.telemetry_consent:
        back4app_endpoint = f'https://parseapi.back4app.com/classes/{class_name}'

        headers = telemetry_config.telemetry_headers
        data = {'fmd_id': telemetry_config.fmd_user, 'session': telemetry_config.telemetry_session}

        for key, value in kwargs.items():
            data[key] = value

        response = requests.post(back4app_endpoint, json=data, headers=headers)
        if response.status_code == 201:  # TODO remove
            print(f'Data posted successfully to {class_name}.', 201)
        else:
            print(f'Failed to post data to {class_name}.', response.status_code)
