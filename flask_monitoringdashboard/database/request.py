"""
Contains all functions that access a Request object.
"""
import time
import datetime
from sqlalchemy import and_, func

from flask_monitoringdashboard.database import Request


def get_latencies_sample(session, endpoint_id, criterion, sample_size=500):
    if getattr(Request, "is_mongo_db", False):
        if criterion and isinstance(criterion, dict):
            criterion = [criterion]
        return list(elem.get("duration") for elem in Request().get_collection(session).find({
            "endpoint_id": endpoint_id,
            "$and": list(criterion)
        } if criterion and len(criterion) > 0 else {"endpoint_id": endpoint_id}).limit(int(sample_size)))
    else:
        query = (
            session.query(Request.duration).filter(Request.endpoint_id == endpoint_id,
                                                   *criterion)
        )
        # return random rows: See https://stackoverflow.com/a/60815
        dialect = session.bind.dialect.name

        if dialect == 'sqlite':
            query = query.order_by(func.random())
        elif dialect == 'mysql':
            query = query.order_by(func.rand())

        query = query.limit(sample_size)

        return [item.duration for item in query.all()]


def get_error_requests_db(session, endpoint_id, *criterion):
    """
    Gets all requests that did not return a 200 status code.

    :param session: session for the database
    :param endpoint_id: ID of the endpoint to be queried
    :param criterion: Optional criteria used to file the requests.
    :return:
    """
    if getattr(Request, "is_mongo_db", False):
        and_condition = [
            {"status_code": {"$ne": None}},
            {"status_code": {"$exists": True}},
            {"status_code": {"$gte": 400}},
            {"status_code": {"$lte": 599}}
        ]
        if len(criterion) > 0:
            and_condition.append({"$and": list(criterion)})
        return list(Request(**elem) for elem in Request().get_collection(session).find({
            "endpoint_id": endpoint_id,
            "$and": and_condition
        }))
    else:
        criteria = and_(
            Request.endpoint_id == endpoint_id,
            Request.status_code.isnot(None),
            Request.status_code >= 400,
            Request.status_code <= 599,
        )
        return session.query(Request).filter(criteria, *criterion).all()


def get_all_request_status_code_counts(session, endpoint_id):
    """
    Gets all the request status code counts.

    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :return: A list of tuples in the form of `(status_code, count)`
    """
    if getattr(Request, "is_mongo_db", False):
        return list((elem["_id"], elem["counting"]) for elem in Request().get_collection(session).aggregate([
            {"$match": {
                "$and": [{"endpoint_id": endpoint_id},
                         {"status_code": {"$ne": None}},
                         {"status_code": {"$exists": True}}]
            }},
            {"$group": {
                "_id": "$status_code",
                "counting": {"$sum": 1}
            }}
        ]))
    else:
        return (
            session.query(Request.status_code, func.count(Request.status_code))
                .filter(Request.endpoint_id == endpoint_id, Request.status_code.isnot(None))
                .group_by(Request.status_code)
                .all()
        )


def get_status_code_frequencies(session, endpoint_id, *criterion):
    """
    Gets the frequencies of each status code.


    :param session: session for the database
    :param endpoint_id: id for the endpoint
    :param criterion: Optional criteria used to file the requests.
    :return: A dict where the key is the status code and the value is the fraction of requests that returned the status
    code. Example: a return value of `{ 200: 105, 404: 3 }` means that status code 200 was returned 105 times and
    404 was returned 3 times.
    """
    if getattr(Request, "is_mongo_db", False):
        and_condition = [
            {"endpoint_id": endpoint_id},
            {"status_code": {"$ne": None}},
            {"status_code": {"$exists": True}}
        ]
        if len(criterion) > 0:
            and_condition.append({"$and": list(criterion)})
        return {elem["_id"]: elem["counting"] for elem in Request().get_collection(session).aggregate([
            {"$match": {
                "$and": and_condition
            }},
            {"$group": {
                "_id": "$status_code",
                "counting": {"$sum": 1}
            }}
        ])}
    else:
        status_code_counts = session.query(Request.status_code, func.count(Request.status_code)) \
            .filter(Request.endpoint_id == endpoint_id, Request.status_code.isnot(None), *criterion) \
            .group_by(Request.status_code).all()
        return dict(status_code_counts)


def add_request(session, duration, endpoint_id, ip, group_by, status_code):
    """ Adds a request to the database. Returns the id.
    :param status_code:  status code of the request
    :param session: session for the database
    :param duration: duration of the request
    :param endpoint_id: id of the endpoint
    :param ip: IP address of the requester
    :param group_by: a criteria by which the requests can be grouped
    :return the id of the request after it was stored in the database
    """
    request = Request(
        endpoint_id=endpoint_id,
        duration=duration,
        ip=ip,
        group_by=group_by,
        status_code=status_code,
    )
    if getattr(Request, "is_mongo_db", False):
        request.get_collection(session).insert_one(request)
    else:
        session.add(request)
        session.commit()
    return request.id


def get_date_of_first_request(session):
    """ Returns the date (as unix timestamp) of the first request since FMD was deployed.
    :param session: session for the database
    :return time of the first request
    """
    if getattr(Request, "is_mongo_db", False):
        result = Request().get_collection(session).find_one(sort=[("time_requested", 1)])
        current_date = result.get("time_requested") if result else None
    else:
        result = session.query(Request.time_requested).order_by(Request.time_requested).first()
        current_date = result[0] if result else None
    if current_date:
        try:
            return int(time.mktime(current_date.timetuple()))
        except:
            return int((current_date-datetime.datetime(1970, 1, 1)).total_seconds())
    return -1


def create_version_criterion(version):
    if getattr(Request, "is_mongo_db", False):
        return [{"version_requested": version}]
    else:
        return Request.version_requested == version


def create_time_based_sample_criterion(start_date, end_date):
    if getattr(Request, "is_mongo_db", False):
        return [{"$and": [{"time_requested": {"$gt": start_date}}, {"time_requested": {"$lte": end_date}}]}]
    else:
        return and_(Request.time_requested > start_date, Request.time_requested <= end_date)


def get_date_of_first_request_version(session, version):
    """ Returns the date (as unix timestamp) of the first request in the current FMD version.
    :param session: session for the database
    :param version: version of the dashboard
    :return time of the first request in that version
    """
    if getattr(Request, "is_mongo_db", False):
        result = Request().get_collection(session).find_one({
            "version_requested": version
        }, sort=[("time_requested", 1)])
        current_date = result.get("time_requested") if result else None
    else:
        result = (
            session.query(Request.time_requested)
                .filter(Request.version_requested == version)
                .order_by(Request.time_requested)
                .first()
        )
        current_date = result[0] if result else None
    if current_date:
        try:
            return int(time.mktime(current_date.timetuple()))
        except:
            return int((current_date-datetime.datetime(1970, 1, 1)).total_seconds())
    return -1
