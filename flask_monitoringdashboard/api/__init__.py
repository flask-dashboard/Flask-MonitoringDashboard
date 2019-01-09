import datetime

from flask import jsonify, request
from plotly.utils import numpy

from flask_monitoringdashboard import blueprint, user_app, config
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.measurement import add_decorator
from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime
from flask_monitoringdashboard.core.utils import get_details, get_endpoint_details
from flask_monitoringdashboard.database import Request, session_scope
from flask_monitoringdashboard.database.count_group import count_requests_group, get_value
from flask_monitoringdashboard.database.data_grouped import get_endpoint_data_grouped
from flask_monitoringdashboard.database.endpoint import get_last_requested, get_endpoints, update_endpoint, \
    get_endpoint_by_name, get_num_requests


@blueprint.route('/api/info')
def get_info():
    with session_scope() as db_session:
        return jsonify(get_details(db_session))


@blueprint.route('/api/overview')
def get_overview():
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    now_local = to_local_datetime(datetime.datetime.utcnow())
    today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = to_utc_datetime(today_local)

    result = []
    with session_scope() as db_session:
        from numpy import median

        hits_today = count_requests_group(db_session, Request.time_requested > today_utc)
        hits_week = count_requests_group(db_session, Request.time_requested > week_ago)
        hits = count_requests_group(db_session)

        median_today = get_endpoint_data_grouped(db_session, median, Request.time_requested > today_utc)
        median_week = get_endpoint_data_grouped(db_session, median, Request.time_requested > week_ago)
        median = get_endpoint_data_grouped(db_session, median)
        access_times = get_last_requested(db_session)

        for endpoint in get_endpoints(db_session):
            result.append({
                'id': endpoint.id,
                'name': endpoint.name,
                'monitor': endpoint.monitor_level,
                'color': get_color(endpoint.name),
                'hits-today': get_value(hits_today, endpoint.id),
                'hits-week': get_value(hits_week, endpoint.id),
                'hits-overall': get_value(hits, endpoint.id),
                'median-today': get_value(median_today, endpoint.id),
                'median-week': get_value(median_week, endpoint.id),
                'median-overall': get_value(median, endpoint.id),
                'last-accessed': get_value(access_times, endpoint.name, default=None)
            })
    return jsonify(result)


@blueprint.route('/api/set_rule', methods=['POST'])
def set_rule():
    """
    the data from the form is validated and processed, such that the required rule is monitored
    """
    endpoint_name = request.form['name']
    value = int(request.form['value'])
    with session_scope() as db_session:
        update_endpoint(db_session, endpoint_name, value=value)

        # Remove wrapper
        original = getattr(user_app.view_functions[endpoint_name], 'original', None)
        if original:
            user_app.view_functions[endpoint_name] = original

    with session_scope() as db_session:
        add_decorator(get_endpoint_by_name(db_session, endpoint_name))

    return 'OK'


@blueprint.route('api/deploy_details')
def deploy_details():
    with session_scope() as db_session:
        details = get_details(db_session)
    details['first-request'] = to_local_datetime(datetime.datetime.fromtimestamp(details['first-request']))
    details['first-request-version'] = to_local_datetime(datetime.datetime.
                                                         fromtimestamp(details['first-request-version']))
    return jsonify(details)


@blueprint.route('api/deploy_config')
def deploy_config():
    return jsonify({
        'database_name': config.database_name,
        'username': config.username,
        'guest_username': config.guest_username,
        'outlier_detection_constant': config.outlier_detection_constant,
        'timezone': str(config.timezone),
        'colors': config.colors
    })


@blueprint.route('api/endpoint_info/<endpoint_id>')
def endpoint_info(endpoint_id):
    with session_scope() as db_session:
        return jsonify(get_endpoint_details(db_session, endpoint_id))


@blueprint.route('api/hourly_load/<start_date>/<end_date>')
# both days must be in the form: yyyy-mm-dd
def hourly_load(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    numdays = (end_date - start_date).days

    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]
    heatmap_data = numpy.zeros((len(hours), numdays))

    start_datetime = to_utc_datetime(datetime.datetime.combine(start_date, datetime.time(0, 0, 0, 0)))
    end_datetime = to_utc_datetime(datetime.datetime.combine(end_date, datetime.time(23, 59, 59)))

    with session_scope() as db_session:
        for time, count in get_num_requests(db_session, None, start_datetime, end_datetime):
            parsed_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            day_index = (parsed_time - start_datetime).days
            hour_index = int(to_local_datetime(parsed_time).strftime('%H'))
            heatmap_data[hour_index][day_index] = count
    return jsonify({
        'days': [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(numdays+1)],
        "data": heatmap_data.tolist()
    })


@blueprint.route('api/test')
def test():
    return jsonify([
        {
            "name": "Baxter Becker",
            "email": "at@eros.co.uk",
            "birthdate": "1981-05-13T18:03:55-07:00"
        },
        {
            "name": "Alvin Sharpe",
            "email": "enim@Phasellus.org",
            "birthdate": "1981-05-12T14:07:04-07:00"
        },
        {
            "name": "Hayes Reynolds",
            "email": "pellentesque@nibhenim.net",
            "birthdate": "1981-05-21T01:35:51-07:00"
        },
        {
            "name": "Myles Wise",
            "email": "diam@diameu.net",
            "birthdate": "1981-05-15T05:30:59-07:00"
        },
        {
            "name": "Declan Ramsey",
            "email": "feugiat.Lorem.ipsum@Donec.org",
            "birthdate": "1981-05-04T20:14:19-07:00"
        },
        {
            "name": "Brenden Nielsen",
            "email": "cras.lorem.lorem@Praesent.edu",
            "birthdate": "1981-05-18T17:56:34-07:00"
        },
        {
            "name": "Todd Chaney",
            "email": "est@Aliquam.ca",
            "birthdate": "1981-05-25T12:53:08-07:00"
        },
        {
            "name": "Ferris Guzman",
            "email": "suspendisse@Cras.org",
            "birthdate": "1981-05-12T02:54:53-07:00"
        },
        {
            "name": "Damian Young",
            "email": "lacinia@interdum.co.uk",
            "birthdate": "1981-05-22T05:55:50-07:00"
        },
        {
            "name": "Steel Bray",
            "email": "mus@Nunc.com",
            "birthdate": "1981-05-18T03:19:31-07:00"
        },
        {
            "name": "Xenos Mack",
            "email": "est@pellentesque.org",
            "birthdate": "1981-05-21T22:30:44-07:00"
        },
        {
            "name": "Kirk Moon",
            "email": "nulla.vulputate@necligula.org",
            "birthdate": "1981-05-22T20:48:14-07:00"
        },
        {
            "name": "Jerry Booth",
            "email": "urna.suscipit.nonummy@odioNam.net",
            "birthdate": "1981-05-25T12:04:01-07:00"
        },
        {
            "name": "Alvin Cook",
            "email": "tincidunt.Donec@augue.com",
            "birthdate": "1981-05-07T16:11:12-07:00"
        },
        {
            "name": "Charles Robertson",
            "email": "tempus.lorem.fringilla@sapienmolestie.com",
            "birthdate": "1981-05-08T06:24:58-07:00"
        },
        {
            "name": "Bruce Russell",
            "email": "faucibus.leo.in@elit.org",
            "birthdate": "1981-05-30T19:49:53-07:00"
        },
        {
            "name": "Rajah Wheeler",
            "email": "elementum@neque.org",
            "birthdate": "1981-05-19T03:37:27-07:00"
        },
        {
            "name": "Nigel Mcbride",
            "email": "magna.et@egetnisi.edu",
            "birthdate": "1981-05-13T09:37:05-07:00"
        },
        {
            "name": "Nathaniel Cleveland",
            "email": "suspendisse@enim.ca",
            "birthdate": "1981-05-05T05:52:08-07:00"
        },
        {
            "name": "Axel Vasquez",
            "email": "libero@commodotinciduntnibh.com",
            "birthdate": "1981-05-17T12:46:30-07:00"
        },
        {
            "name": "Colby Russell",
            "email": "et.lacinia@purus.com",
            "birthdate": "1981-05-05T12:35:45-07:00"
        },
        {
            "name": "Beck Sharpe",
            "email": "velit.Cras.lorem@tristique.ca",
            "birthdate": "1981-05-22T04:37:09-07:00"
        },
        {
            "name": "Orson Foley",
            "email": "eu@nunc.com",
            "birthdate": "1981-05-25T07:15:54-07:00"
        },
        {
            "name": "Magee Duncan",
            "email": "neque.et.nunc@erat.co.uk",
            "birthdate": "1981-05-24T16:55:55-07:00"
        },
        {
            "name": "Keith Knapp",
            "email": "sem@ligula.edu",
            "birthdate": "1981-05-28T03:49:50-07:00"
        },
        {
            "name": "Hilel Klein",
            "email": "dis.parturient.montes@Donec.edu",
            "birthdate": "1981-05-16T05:06:34-07:00"
        },
        {
            "name": "Zachary Rutledge",
            "email": "elit.sed.consequat@nonummy.ca",
            "birthdate": "1981-05-22T01:02:56-07:00"
        },
        {
            "name": "Kennan Hurst",
            "email": "vitae.diam@faucibus.co.uk",
            "birthdate": "1981-05-27T07:28:04-07:00"
        },
        {
            "name": "Brent Gonzalez",
            "email": "pretium@mollis.net",
            "birthdate": "1981-05-28T17:19:00-07:00"
        },
        {
            "name": "Igor Porter",
            "email": "pellentesque@metusvitaevelit.edu",
            "birthdate": "1981-05-20T16:50:50-07:00"
        },
        {
            "name": "Derek Talley",
            "email": "vitae.odio.sagittis@eget.co.uk",
            "birthdate": "1981-05-18T14:29:06-07:00"
        },
        {
            "name": "Wayne Branch",
            "email": "auctor.quis.tristique@a.co.uk",
            "birthdate": "1981-05-16T05:19:18-07:00"
        },
        {
            "name": "Allen Trevino",
            "email": "phasellus.at@velit.org",
            "birthdate": "1981-05-30T04:35:15-07:00"
        },
        {
            "name": "Oscar Gilliam",
            "email": "curabitur.vel.lectus@adipiscingelit.edu",
            "birthdate": "1981-05-10T09:09:43-07:00"
        },
        {
            "name": "Macon Avila",
            "email": "pede@erosnonenim.com",
            "birthdate": "1981-05-21T23:06:49-07:00"
        }
    ])
