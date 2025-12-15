from datetime import timedelta

from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard.database import CustomGraph, CustomGraphData, row2dict


def get_graph_id_from_name(session, name):
    """
    :param session: session for the database
    :param name: name of the graph (must be unique)
    :return: the graph_id corresponding to the name. If the name does not exists in the db,
             a new graph is added to the database.
    """
    try:
        result = session.query(CustomGraph).filter(CustomGraph.title == name).one()
    except NoResultFound:
        result = CustomGraph(title=name)
        session.add(result)
        session.flush()
    session.expunge(result)
    return result.graph_id


def add_value(session, graph_id, value):
    data = CustomGraphData(graph_id=graph_id, value=value)
    session.add(data)


def get_graphs(session):
    return session.query(CustomGraph).all()


def get_graph_data(session, graph_id, start_date, end_date):
    """
    :param session: session for the database
    :param graph_id: id to filter on
    :param start_date: Datetime object that denotes the beginning of the interval
    :param end_date: Datetime object that denotes the end of the interval
    :return: A list with values retrieved from the database
    """
    return [
        row2dict(row)
        for row in session.query(CustomGraphData)
        .filter(
            CustomGraphData.graph_id == graph_id,
            CustomGraphData.time >= start_date,
            CustomGraphData.time < end_date + timedelta(days=1),
        )
        .all()
    ]
