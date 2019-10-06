from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard.database import CustomGraph, CustomGraphData, row2dict


def get_graph_id_from_name(db_session, name):
    """
    :param db_session: session for the database
    :param name: name of the graph (must be unique)
    :return: the graph_id corresponding to the name. If the name does not exists in the db,
             a new graph is added to the database.
    """
    try:
        result = db_session.query(CustomGraph).filter(CustomGraph.title == name).one()
    except NoResultFound:
        result = CustomGraph(title=name)
        db_session.add(result)
        db_session.flush()
    db_session.expunge(result)
    return result.graph_id


def add_value(db_session, graph_id, value):
    data = CustomGraphData(graph_id=graph_id, value=value)
    db_session.add(data)


def get_graphs(db_session):
    return db_session.query(CustomGraph).all()


def get_graph_data(db_session, graph_id, start_date, end_date):
    """
    :param db_session: session for the database
    :param graph_id: id to filter on
    :param start_date: Datetime object that denotes the beginning of the interval
    :param end_date: Datetime object that denotes the end of the interval
    :return: A list with values retrieved from the database
    """
    return [
        row2dict(row)
        for row in db_session.query(CustomGraphData)
        .filter(
            CustomGraphData.graph_id == graph_id,
            CustomGraphData.time >= start_date,
            CustomGraphData.time <= end_date,
        )
        .all()
    ]
