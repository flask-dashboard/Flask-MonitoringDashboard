from flask_monitoringdashboard.database import DatabaseConnectionWrapper


def add_outlier(session, request_id, cpu_percent, memory, stacktrace, request):
    """
    Adds an Outlier object in the database.
    :param session: session for the database
    :param request_id: id of the request
    :param cpu_percent: cpu load of the server when processing the request
    :param memory: memory load of the server when processing the request
    :param stacktrace: stack trace of the request
    :param request: triple containing the headers, environment and url
    """
    database_connection_wrapper = DatabaseConnectionWrapper()
    headers, environ, url = request
    database_connection_wrapper.database_connection.outlier_query(session).create_outlier_record(
        database_connection_wrapper.database_connection.outlier(
            request_id=request_id,
            request_header=headers,
            request_environment=environ,
            request_url=url,
            cpu_percent=cpu_percent,
            memory=memory,
            stacktrace=stacktrace,
        )
    )


def get_outliers_sorted(session, endpoint_id, offset, per_page):
    """
    Gets a list of Outlier objects for a certain endpoint, sorted by most recent request time
    :param session: session for the database
    :param endpoint_id: id of the endpoint for filtering the requests
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return list of Outlier objects of a specific endpoint
    """
    return DatabaseConnectionWrapper().database_connection.outlier_query(session).get_outliers_sorted(endpoint_id,
                                                                                                      offset,
                                                                                                      per_page)


def get_outliers_cpus(session, endpoint_id):
    """
    Gets list of CPU loads of all outliers of a certain endpoint
    :param session: session for the database
    :param endpoint_id: id of the endpoint
    :return list of cpu percentages as strings
    """
    return DatabaseConnectionWrapper().database_connection.outlier_query(session).get_outliers_cpus(endpoint_id)
