from flask_monitoringdashboard.database import DatabaseConnectionWrapper
from flask_monitoringdashboard.database.custom_graph import add_value, get_graph_id_from_name
from flask_monitoringdashboard.core import custom_graph
import time
import datetime
import random
import math


db = DatabaseConnectionWrapper()


def test_create_graph_and_add_values(session):
    db.database_connection.custom_graph_query(session).delete_all_data()
    db.database_connection.custom_graph_query(session).commit()
    graph_id = get_graph_id_from_name("TEST GRAPH")
    graph_id_1 = get_graph_id_from_name("TEST GRAPH")
    assert graph_id_1 == graph_id
    add_value(graph_id, "10")
    time.sleep(10)
    add_value(graph_id, "15")
    all_graph_value = db.database_connection.custom_graph_query(session).find_all(
        db.database_connection.custom_graph_data)
    assert len(all_graph_value) == 2
    assert all_graph_value[1].time - all_graph_value[0].time >= datetime.timedelta(seconds=10)


def test_scheduler(session):
    custom_graph.scheduler.start()
    db.database_connection.custom_graph_query(session).delete_all_data()
    db.database_connection.custom_graph_query(session).commit()
    graph_id = get_graph_id_from_name("TEST GRAPH")

    def every_ten_seconds():
        return int(random.random() * 100 // 10)

    every_ten_seconds_schedule = {'seconds': 1}
    custom_graph.add_background_job(every_ten_seconds, graph_id, "interval", **every_ten_seconds_schedule)
    time.sleep(5)
    custom_graph.scheduler.shutdown()
    all_graph_value = db.database_connection.custom_graph_query(session).find_all(
        db.database_connection.custom_graph_data)
    assert len(all_graph_value) >= 5
    for index in range(0, len(all_graph_value) - 1):
        print(all_graph_value[index+1].time - all_graph_value[index].time)
        assert (all_graph_value[index+1].time - all_graph_value[index].time) >= datetime.timedelta(seconds=0.8)
