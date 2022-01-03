from sqlalchemy import func, distinct

from flask_monitoringdashboard.database import Request, StackLine, Outlier


def count_rows(session, column, *criterion):
    """
    Count the number of rows of a specified column.
    :param session: session for the database
    :param column: column to count
    :param criterion: where-clause of the query
    :return: number of rows
    """

    if getattr(Request, "is_mongo_db", False):
        return Request().get_collection(session).count_documents({"$and": list(criterion)}
                                                                 if len(criterion) > 0 else {})
    else:
        return session.query(func.count(distinct(column))).filter(*criterion).scalar()


def count_requests(session, endpoint_id, *where):
    """
    Return the number of hits for a specific endpoint (possible with more filter arguments).
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :param where: additional arguments
    """
    return count_rows(session,
                      Request.id if not getattr(Request, "is_mongo_db", False) else "id",
                      Request.endpoint_id == endpoint_id if not getattr(Request, "is_mongo_db", False) else
                      {"endpoint_id": endpoint_id},
                      *where)


def count_total_requests(session, *where):
    """
    Return the number of total hits
    :param session: session for the database
    :param where: additional arguments
    """
    return count_rows(session,
                      Request.id if not getattr(Request, "is_mongo_db", False) else "id",
                      *where)


def count_outliers(session, endpoint_id):
    """
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return: An integer with the number of rows in the Outlier-table.
    """
    if getattr(Request, "is_mongo_db", False):
        return Outlier().get_collection(session).count_documents({"endpoint_id": endpoint_id})
    else:
        return count_rows(session,
                          Request.id,
                          Request.endpoint_id == endpoint_id,
                          Request.outlier)


def count_profiled_requests(session, endpoint_id):
    """
    Count the number of profiled requests for a certain endpoint
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return: An integer
    """
    if getattr(Request, "is_mongo_db", False):
        return len(StackLine().get_collection(session).distinct("request_id", {"endpoint_id": endpoint_id}))
    else:
        return (
            session.query(func.count(distinct(StackLine.request_id)))
            .filter(Request.endpoint_id == endpoint_id)
            .join(Request.stack_lines)
            .scalar()
        )
