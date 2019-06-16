import datetime

from flask import jsonify

from flask_monitoringdashboard.controllers.requests import get_num_requests_data, get_hourly_load
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard import blueprint


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


@blueprint.route('/api/hourly_load/<start_date>/<end_date>')
@blueprint.route('/api/hourly_load/<start_date>/<end_date>/<endpoint_id>')
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
