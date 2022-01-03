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
    if getattr(CustomGraph, "is_mongo_db", False):
        collection = CustomGraph().get_collection(session)
        result = collection.find_one({
            "title": name
        })
        if not result:
            result = CustomGraph(title=name)
            collection.insert_one(result)
        result = CustomGraph(**result)
    else:
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
    if getattr(CustomGraphData, "is_mongo_db", False):
        data.get_collection(session).update_one(
            {"graph_id": graph_id},
            {"$set": {"value": value}}
        )
    else:
        session.add(data)


def get_graphs(session):
    if getattr(CustomGraph, "is_mongo_db", False):
        return list(CustomGraph(**elem) for elem in CustomGraph().get_collection(session).find({}))
    else:
        try:
            return session.query(CustomGraph).all()
        finally:
            session.expunge_all()


def get_graph_data(session, graph_id, start_date, end_date):
    """
    :param session: session for the database
    :param graph_id: id to filter on
    :param start_date: Datetime object that denotes the beginning of the interval
    :param end_date: Datetime object that denotes the end of the interval
    :return: A list with values retrieved from the database
    """
    if getattr(CustomGraphData, "is_mongo_db", False):
        rows = list(CustomGraphData(**elem) for elem in CustomGraphData().get_collection(session).find({
            "graph_id": graph_id,
            "$and": [{"time": {"$gte": start_date}}, {"time": {"$lt": end_date + timedelta(days=1)}}]
        }))
    else:
        rows = session.query(CustomGraphData).filter(
            CustomGraphData.graph_id == graph_id,
            CustomGraphData.time >= start_date,
            CustomGraphData.time < end_date + timedelta(days=1),
        ).all()
    return [
        row2dict(row)
        for row in rows
    ]
