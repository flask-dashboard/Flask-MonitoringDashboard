from flask_monitoringdashboard.database import DatabaseConnectionWrapper


def get_graph_id_from_name(name):
    """
    :param name: name of the graph (must be unique)
    :return: the graph_id corresponding to the name. If the name does not exists in the db,
             a new graph is added to the database.
    """
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        return database_connection_wrapper.database_connection.custom_graph_query(session).\
            find_or_create_graph(name).graph_id


def add_value(graph_id, value):
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        database_connection_wrapper.database_connection.custom_graph_query(session).create_obj(
            database_connection_wrapper.database_connection.custom_graph_data(graph_id=graph_id, value=value))


def get_graphs():
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        return [
            database_connection_wrapper.database_connection.row2dict(elem) for elem in
            database_connection_wrapper.database_connection.custom_graph_query(session).get_graphs()
            if elem is not None
        ]


def get_graph_data(graph_id, start_date, end_date):
    """
    :param graph_id: id to filter on
    :param start_date: Datetime object that denotes the beginning of the interval
    :param end_date: Datetime object that denotes the end of the interval
    :return: A list with values retrieved from the database
    """
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        return database_connection_wrapper.database_connection.custom_graph_query(session).get_graph_data(graph_id,
                                                                                                          start_date,
                                                                                                          end_date)
