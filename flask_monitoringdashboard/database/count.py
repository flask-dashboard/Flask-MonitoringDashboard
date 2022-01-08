from flask_monitoringdashboard.database import DatabaseConnectionWrapper


def count_rows(session, column, *criterion):
    """
    Count the number of rows of a specified column.
    :param session: session for the database
    :param column: column to count
    :param criterion: where-clause of the query
    :return: number of rows
    """
    return DatabaseConnectionWrapper().database_connection.count_queries(session).count_rows(column, *criterion)


def count_requests(session, endpoint_id, *where):
    """
    Return the number of hits for a specific endpoint (possible with more filter arguments).
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :param where: additional arguments
    """
    return DatabaseConnectionWrapper().database_connection.count_queries(session).count_requests(endpoint_id, *where)


def count_total_requests(session, *where):
    """
    Return the number of total hits
    :param session: session for the database
    :param where: additional arguments
    """
    return DatabaseConnectionWrapper().database_connection.count_queries(session).count_total_requests(*where)


def count_outliers(session, endpoint_id):
    """
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return: An integer with the number of rows in the Outlier-table.
    """
    return DatabaseConnectionWrapper().database_connection.count_queries(session).count_outliers(endpoint_id)


def count_profiled_requests(session, endpoint_id):
    """
    Count the number of profiled requests for a certain endpoint
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return: An integer
    """
    return DatabaseConnectionWrapper().database_connection.count_queries(session).count_profiled_requests(endpoint_id)
