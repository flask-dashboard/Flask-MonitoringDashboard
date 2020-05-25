from datetime import datetime, timedelta

from flask_monitoringdashboard.database import CustomGraph


def test_custom_graphs(dashboard_user, custom_graph, session):
    response = dashboard_user.get('dashboard/api/custom_graphs')
    assert response.status_code == 200

    data = response.json
    assert len(data) == session.query(CustomGraph).count()

    [data_custom_graph] = [graph for graph in data if graph['graph_id'] == str(custom_graph.graph_id)]
    assert data_custom_graph['title'] == custom_graph.title
    assert data_custom_graph['time_added'] == str(custom_graph.time_added)
    assert data_custom_graph['version_added'] == custom_graph.version_added


def test_custom_graph_data(dashboard_user, custom_graph, custom_graph_data):
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    response = dashboard_user.get('dashboard/api/custom_graph/{id}/{start}/{end}'.format(
        id=custom_graph.graph_id,
        start=yesterday.strftime('%Y-%m-%d'),
        end=today.strftime('%Y-%m-%d'),
    ))
    assert response.status_code == 200
    [data] = response.json
    assert data['graph_id'] == str(custom_graph.graph_id)
    assert data['id'] == str(custom_graph_data.id)
    assert data['time'] == str(custom_graph_data.time)
    assert data['value'] == str(custom_graph_data.value)
