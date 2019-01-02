import datetime

from flask import jsonify

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime
from flask_monitoringdashboard.core.utils import get_details
from flask_monitoringdashboard.database import Request, session_scope
from flask_monitoringdashboard.database.count_group import count_requests_group, get_value
from flask_monitoringdashboard.database.data_grouped import get_endpoint_data_grouped
from flask_monitoringdashboard.database.endpoint import get_last_requested, get_endpoints


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
