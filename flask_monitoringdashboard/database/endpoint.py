"""
Contains all functions that access an Endpoint object
"""
import datetime
from collections import defaultdict

from sqlalchemy import func, desc, and_
from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database import Request, Endpoint


def get_num_requests(session, endpoint_id, start_date, end_date):
    """
    Returns a list with all dates on which an endpoint is accessed.
    :param session: session for the database
    :param endpoint_id: if None, the result is the sum of all endpoints
    :param start_date: datetime.date object
    :param end_date: datetime.date object
    :return list of dates
    """
    if getattr(Request, "is_mongo_db", False):
        query = {
            "$and": [{"time_requested": {"$gte": start_date}}, {"time_requested": {"$lte": end_date}}]
        }
        if endpoint_id:
            query["endpoint_id"] = endpoint_id
        return group_request_times(list(r["time_requested"] for r in Request().get_collection(session).find(query)))
    else:
        query = session.query(Request.time_requested)
        if endpoint_id:
            query = query.filter(Request.endpoint_id == endpoint_id)
        result = query.filter(
            Request.time_requested >= start_date, Request.time_requested <= end_date
        ).all()

        return group_request_times([r[0] for r in result])


def group_request_times(datetimes):
    """
    Returns a list of tuples containing the number of hits per hour
    :param datetimes: list of datetime objects
    :return list of tuples ('%Y-%m-%d %H:00:00', count)
    """
    hours_dict = defaultdict(int)
    for dt in datetimes:
        round_time = dt.strftime('%Y-%m-%d %H:00:00')
        hours_dict[round_time] += 1
    return hours_dict.items()


def get_users(session, endpoint_id, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to
    filter the most used distinct.
    :param session: session for the database
    :param endpoint_id: the id of the endpoint to filter on
    :param limit: the max number of results
    :return a list of tuples (group_by, hits)
    """
    if getattr(Request, "is_mongo_db", False):
        query = [
            {"$match": {"endpoint_id": endpoint_id}},
            {"$group": {"_id": "$group_by", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ]
        if limit:
            query.append({"$limit": int(limit)})
        results = Request().get_collection(session).aggregate(query)
        return [(result["_id"], result["counting"]) for result in results]
    else:
        query = (
            session.query(Request.group_by, func.count(Request.group_by))
            .filter(Request.endpoint_id == endpoint_id)
            .group_by(Request.group_by)
            .order_by(desc(func.count(Request.group_by)))
        )
        if limit:
            query = query.limit(limit)
        result = query.all()
        session.expunge_all()
        return result


def get_ips(session, endpoint_id, limit=None):
    """
    Returns a list with the distinct group-by from a specific endpoint. The limit is used to
    filter the most used distinct.
    :param session: session for the database
    :param endpoint_id: the endpoint_id to filter on
    :param limit: the number of
    :return a list with the group_by as strings.
    """
    if getattr(Request, "is_mongo_db", False):
        query = [
            {"$match": {"endpoint_id": endpoint_id}},
            {"$group": {"_id": "$ip", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ]
        if limit:
            query.append({"$limit": int(limit)})
        results = Request().get_collection(session).aggregate(query)
        return [(result["_id"], result["counting"]) for result in results]
    else:
        query = (
            session.query(Request.ip, func.count(Request.ip))
            .filter(Request.endpoint_id == endpoint_id)
            .group_by(Request.ip)
            .order_by(desc(func.count(Request.ip)))
        )
        if limit:
            query = query.limit(limit)
        result = query.all()
        session.expunge_all()
        return result


def get_endpoint_by_name(session, endpoint_name):
    """
    Returns the Endpoint object from a given endpoint_name.
    If the result doesn't exist in the database, a new row is added.
    :param session: session for the database
    :param endpoint_name: string with the endpoint name
    :return Endpoint object
    """
    if getattr(Endpoint, "is_mongo_db", False):
        current_endpoint = Endpoint(name=endpoint_name)
        endpoint_collection = current_endpoint.get_collection(session)
        result = endpoint_collection.find_one({"name": endpoint_name})
        if not result:
            endpoint_collection.insert_one(current_endpoint)
            result = current_endpoint
        else:
            result = Endpoint(**result)
            result.time_added = to_local_datetime(result.time_added)
            result.last_requested = to_local_datetime(result.last_requested)
    else:
        try:
            result = session.query(Endpoint).filter(Endpoint.name == endpoint_name).one()
            result.time_added = to_local_datetime(result.time_added)
            result.last_requested = to_local_datetime(result.last_requested)
        except NoResultFound:
            result = Endpoint(name=endpoint_name)
            session.add(result)
            session.flush()
        session.expunge(result)
    return result


def get_endpoint_by_id(session, endpoint_id):
    """
    Returns the Endpoint object from a given endpoint id.
    :param session: session for the database
    :param endpoint_id: id of the endpoint.
    :return Endpoint object
    """
    if getattr(Endpoint, "is_mongo_db", False):
        return Endpoint(**Endpoint().get_collection(session).find_one({"id": endpoint_id}))
    else:
        result = session.query(Endpoint).filter(Endpoint.id == endpoint_id).one()
        session.expunge(result)
        return result


def update_endpoint(session, endpoint_name, value):
    """
    Updates the value of a specific Endpoint.
    :param session: session for the database
    :param endpoint_name: name of the endpoint
    :param value: new monitor level
    """
    if getattr(Endpoint, "is_mongo_db", False):
        Endpoint().get_collection(session).update_one({"name": endpoint_name}, {"$set": {"monitor_level": value}})
    else:
        session.query(Endpoint).filter(Endpoint.name == endpoint_name).update(
            {Endpoint.monitor_level: value}
        )
        session.flush()


def get_last_requested(session):
    """
    Returns the accessed time of all endpoints.
    :param session: session for the database
    :return list of tuples with name of the endpoint and date it was last used
    """
    if getattr(Endpoint, "is_mongo_db", False):
        endpoint_collection = Endpoint().get_collection(session)
        return list((elem["name"], elem.get("last_requested")) for elem in endpoint_collection.find())
    else:
        result = session.query(Endpoint.name, Endpoint.last_requested).all()
        session.expunge_all()
    return result


def update_last_requested(session, endpoint_name, timestamp=None):
    """
    Updates the timestamp of last access of the endpoint.
    :param session: session for the database
    :param endpoint_name: name of the endpoint
    :param timestamp: optional timestamp. If not given, timestamp is current time
    """
    ts = timestamp if timestamp else datetime.datetime.utcnow()
    if getattr(Endpoint, "is_mongo_db", False):
        Endpoint().get_collection(session).update_one({"name": endpoint_name}, {"$set": {"last_requested": ts}})
    else:
        session.query(Endpoint).filter(Endpoint.name == endpoint_name).update(
            {Endpoint.last_requested: ts}
        )


def get_endpoints(session):
    """
    Returns all Endpoint objects from the database.
    :param session: session for the database
    :return list of Endpoint objects, sorted on the number of requests (descending)
    """
    if getattr(Endpoint, "is_mongo_db", False):
        endpoint_collection = Endpoint().get_collection(session)
        endpoints = {endpoint["id"]: endpoint for endpoint in endpoint_collection.find({})}
        endpoint_keys = list(endpoints.keys())
        request_collection = Request().get_collection(session)
        results = request_collection.aggregate([
            {"$match": {"endpoint_id": {"$in": endpoint_keys}}},
            {"$group": {"_id": "$endpoint_id", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ])
        output = []
        for result in results:
            output.append(Endpoint(**endpoints[result["_id"]]))
            endpoint_keys.remove(result["_id"])
        for endpoint_key in endpoint_keys:
            output.append(Endpoint(**endpoints[endpoint_key]))
        return output
    else:
        return (
            session.query(Endpoint)
            .outerjoin(Request)
            .group_by(Endpoint.id)
            .order_by(desc(func.count(Request.endpoint_id)))
        )


def get_endpoints_hits(session):
    """
    Returns all endpoint names and total hits from the database.
    :param session: session for the database
    :return list of (endpoint name, total hits) tuples
    """
    if getattr(Endpoint, "is_mongo_db", False):
        endpoint_collection = Endpoint().get_collection(session)
        endpoints = {endpoint["id"]: endpoint["name"] for endpoint in endpoint_collection.find({})}
        request_collection = Request().get_collection(session)
        results = request_collection.aggregate([
            {"$match": {"endpoint_id": {"$in": list(endpoints.keys())}}},
            {"$group": {"_id": "$endpoint_id", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ])
        return [(endpoints[result["_id"]], result["counting"]) for result in results]
    else:
        return (
            session.query(Endpoint.name, func.count(Request.endpoint_id))
            .join(Request)
            .group_by(Endpoint.name)
            .order_by(desc(func.count(Request.endpoint_id)))
            .all()
        )


def get_avg_duration(session, endpoint_id):
    """ Returns the average duration of all the requests of an endpoint. If there are no requests
        for that endpoint, it returns 0.
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return average duration
    """
    if getattr(Endpoint, "is_mongo_db", False):
        request_collection = Request().get_collection(session)
        results = list(request_collection.aggregate([
            {"$match": {"endpoint_id": endpoint_id}},
            {"$group": {"_id": "$endpoint_id", "average": {"$avg": "$duration"}}}
        ]))
        if results and results[0]:
            return results[0]["average"]
    else:
        result = (
            session.query(func.avg(Request.duration).label('average'))
            .filter(Request.endpoint_id == endpoint_id)
            .one()
        )
        if result[0]:
            return result[0]
    return 0


def get_endpoint_averages(session):
    """ Returns the average duration of all endpoints. If there are no requests for an endpoint,
        the average will be none.
    :param session: session for the database
    :return tuple of (endpoint_name, avg_duration)
    """
    if getattr(Endpoint, "is_mongo_db", False):
        endpoint_collection = Endpoint().get_collection(session)
        endpoints = {endpoint["id"]: endpoint["name"] for endpoint in endpoint_collection.find({})}
        request_collection = Request().get_collection(session)
        results = request_collection.aggregate([
            {"$match": {"endpoint_id": {"$in": list(endpoints.keys())}}},
            {"$group": {"_id": "$endpoint_id", "average": {"$avg": "$duration"}}}
        ])
        return [(endpoints[result["_id"]], result["average"]) for result in results]
    else:
        result = (
            session.query(Endpoint.name, func.avg(Request.duration).label('average'))
            .outerjoin(Request)
            .group_by(Endpoint.name)
            .all()
        )
        return result


def generate_request_error_hits_criterion():
    if getattr(Request, "is_mongo_db", False):
        return {
            "$and": [{"status_code": {"$gte": 400}}, {"status_code": {"$lt": 600}}]
        }
    else:
        return and_(Request.status_code >= 400, Request.status_code < 600)


def filter_by_endpoint_id(endpoint_id):
    if getattr(Request, "is_mongo_db", False):
        return {"endpoint_id": endpoint_id}
    else:
        return Request.endpoint_id == endpoint_id


def filter_by_time(current_time, hits_criterion=None):
    if getattr(Request, "is_mongo_db", False):
        return {
            "$and": [{"time_requested": {"$gte": current_time}}, hits_criterion] if hits_criterion else
                    [{"time_requested": {"$gte": current_time}}]
        }
    else:
        if hits_criterion is None:
            return Request.time_requested > current_time
        else:
            return and_(Request.time_requested > current_time, hits_criterion)
