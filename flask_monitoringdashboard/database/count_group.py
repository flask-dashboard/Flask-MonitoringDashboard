import datetime

from sqlalchemy import func

from flask_monitoringdashboard.core.timezone import to_utc_datetime
from flask_monitoringdashboard.database import Request


def count_rows_group(session, column, *criterion):
    """
    Count the number of rows of a specified column
    :param session: session for the database
    :param column: column to count
    :param criterion: where-clause of the query
    :return list with the number of rows per endpoint
    """
    if getattr(Request, "is_mongo_db", False):
        query = [
            {"$group": {
                "_id": "$endpoint_id",
                "counting": {"$sum": 1}
            }}
        ]
        if len(criterion) > 0:
            query.insert(0, {"$match": {"$and": list(criterion)}})
        return list((elem["_id"], elem["counting"]) for elem in Request().get_collection(session).aggregate(query))
    else:
        return (
            session.query(Request.endpoint_id, func.count(column))
            .filter(*criterion)
            .group_by(Request.endpoint_id)
            .all()
        )


def get_value(tuples, name, default=0):
    """
    :param tuples: must be structured as: [(a, b), (c, d), ..]
    :param name: name to filter on, e.g.: if name == a, it returns b
    :param default: returned if the name was not found in the list
    :return value corresponding to the name in the list.
    """
    if tuples:
        for key, value in tuples:
            if key == name:
                return value
    return default


def count_requests_group(session, *where):
    """
    Return the number of hits for all endpoints (possible with more filter arguments).
    :param session: session for the database
    :param where: additional arguments
    """
    return count_rows_group(session,
                            Request.id if not getattr(Request, "is_mongo_db", False) else "id",
                            *where)


def count_requests_per_day(session, list_of_days):
    """ Return the number of hits for all endpoints per day.
    :param session: session for the database
    :param list_of_days: list with datetime.datetime objects. """
    result = []
    for day in list_of_days:
        dt_begin = to_utc_datetime(datetime.datetime.combine(day, datetime.time(0, 0, 0)))
        dt_end = dt_begin + datetime.timedelta(days=1)

        result.append(
            count_rows_group(
                session,
                Request.id,
                Request.time_requested >= dt_begin,
                Request.time_requested < dt_end,
            ) if not getattr(Request, "is_mongo_db", False) else count_rows_group(
                session,
                "id",
                {"$and": [{"time_requested": {"$gte": dt_begin}}, {"time_requested": {"$lt": dt_end}}]}
            )
        )
    return result
