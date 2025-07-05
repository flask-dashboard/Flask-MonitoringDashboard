import datetime
import requests
import functools
import sys

from sqlalchemy import func
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, SQLAlchemyError

from flask_monitoringdashboard import telemetry_config
from flask_monitoringdashboard.core.config import TelemetryConfig
from flask_monitoringdashboard.core.blueprints import get_blueprint
from flask_monitoringdashboard.core.utils import get_details
from flask_monitoringdashboard.database import TelemetryUser, Endpoint


def get_telemetry_user(session):
    """Return a telemetry user object"""
    try:
        return session.query(TelemetryUser).one()

    except (MultipleResultsFound, NoResultFound):
        session.query(TelemetryUser).delete()
        initialize_telemetry_session(session)

    except SQLAlchemyError as e:
        session.rollback()
        initialize_telemetry_session(session)

    finally:
        return session.query(TelemetryUser).one()


def collect_general_telemetry_data(session, telemetry_user):
    """
    Collects telemetry data and posts it to the remote database
    """
    # collect endpoint and blueprint data
    endpoints = session.query(Endpoint.name).all()
    blueprints = set(get_blueprint(endpoint) for endpoint, in endpoints)
    no_of_endpoints = len(endpoints)
    no_of_blueprints = len(blueprints)

    # collect the amount of endpoints with their respective monitoring levels
    counts = (
        session.query(Endpoint.monitor_level, func.count(Endpoint.monitor_level))
        .group_by(Endpoint.monitor_level)
        .all()
    )
    counts_dict = dict(counts)
    level_zeros_count = counts_dict.get(0, 0)
    level_ones_count = counts_dict.get(1, 0)
    level_twos_count = counts_dict.get(2, 0)
    level_threes_count = counts_dict.get(3, 0)

    # Get details including the dashboard version
    details = get_details(session)
    dashboard_version = details['dashboard-version']

    # Get python version
    python_version = sys.version

    data = {'endpoints': no_of_endpoints,
            'blueprints': no_of_blueprints,
            'time_initialized': telemetry_user.last_initialized.strftime('%Y-%m-%d %H:%M:%S'),
            'monitoring_0': level_zeros_count,
            'monitoring_1': level_ones_count,
            'monitoring_2': level_twos_count,
            'monitoring_3': level_threes_count,
            'dashboard_version': dashboard_version,
            'python_version': python_version,
            }

    # post user data
    post_to_back_if_telemetry_enabled('UserSession', **data)


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
            telemetry_user.times_initialized += 1
            telemetry_user.last_initialized = datetime.datetime.now(datetime.timezone.utc)
            session.commit()

        # reset telemetry if declined in previous session
        if telemetry_user.monitoring_consent == TelemetryConfig.REJECTED:
            telemetry_user.monitoring_consent = TelemetryConfig.NOT_ANSWERED
            session.commit()

        # check if telemetry's been agreed on
        telemetry_config.telemetry_consent = True if telemetry_user.monitoring_consent == TelemetryConfig.ACCEPTED else False

        # save the telemetry_config for quick access
        telemetry_config.fmd_user = telemetry_user.id
        telemetry_config.telemetry_initialized = True
        telemetry_config.telemetry_session = telemetry_user.times_initialized

        # collect the data and send it to the remote database
        collect_general_telemetry_data(session, telemetry_user)

    except (MultipleResultsFound, NoResultFound) as e:
        print(e)
        session.query(TelemetryUser).delete()
        initialize_telemetry_session(session)

    except SQLAlchemyError as e:
        print(e)
        session.rollback()


@functools.lru_cache(maxsize=None)
def fetch_ip_from_github(file_url):
    """
    Fetches the IP address from a text file hosted on GitHub and caches the result.
    
    Args:
    file_url (str): URL to the raw version of the GitHub hosted text file containing the IP address.
    
    Returns:
    str: IP address and port as a string, or None if unable to fetch.
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.text.strip()  # Assuming the file contains the IP address and port in the format "IP:PORT"
    except requests.RequestException:
        return None


def post_to_back_if_telemetry_enabled(class_name='Endpoints', **kwargs):
    """
    Function to send data to server, with dynamic IP fetching.
    If the IP cannot be fetched, the function will silently exit without sending data.
    """
    if telemetry_config.telemetry_consent or class_name == 'FollowUp':
        github_file_url = 'https://raw.githubusercontent.com/flask-dashboard/fmd-telemetry/master/ip_address'
        parse_server_ip = fetch_ip_from_github(github_file_url)
        if parse_server_ip is None:
            return  # Exit silently if no IP is fetched
        
        parse_server_endpoint = f'http://{parse_server_ip}/parse/classes/{class_name}'
        headers = telemetry_config.telemetry_headers
        data = {'fmd_id': telemetry_config.fmd_user, 'session': telemetry_config.telemetry_session}
        for key, value in kwargs.items():
            data[key] = value

        try:
            response = requests.post(parse_server_endpoint, json=data, headers=headers, timeout=1)
            return response
        except requests.exceptions.ConnectionError as e:
            return None

 