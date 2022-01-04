from flask_monitoringdashboard.database import CustomGraphData, CustomGraphQuery


def get_graph_id_from_name(session, name):
    """
    :param session: session for the database
    :param name: name of the graph (must be unique)
    :return: the graph_id corresponding to the name. If the name does not exists in the db,
             a new graph is added to the database.
    """
    return CustomGraphQuery(session).find_or_create_graph(name).graph_id


def add_value(session, graph_id, value):
    CustomGraphQuery(session).create_obj(CustomGraphData(graph_id=graph_id, value=value))


def get_graphs(session):
    return CustomGraphQuery(session).get_graphs()


def get_graph_data(session, graph_id, start_date, end_date):
    """
    :param session: session for the database
    :param graph_id: id to filter on
    :param start_date: Datetime object that denotes the beginning of the interval
    :param end_date: Datetime object that denotes the end of the interval
    :return: A list with values retrieved from the database
    """
    return CustomGraphQuery(session).get_graph_data(graph_id, start_date, end_date)
