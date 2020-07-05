from flask_monitoringdashboard.database import Request


def test_deployment(dashboard_user, session, config):
    response = dashboard_user.get('dashboard/api/deploy_details')
    assert response.status_code == 200

    data = response.json
    assert data['config-version'] == config.version
    assert data['link'] == 'dashboard'
    assert data['total-requests'] == session.query(Request).count()


def test_deployment_config(dashboard_user, config):
    response = dashboard_user.get('dashboard/api/deploy_config')
    assert response.status_code == 200

    data = response.json
    assert data['database_name'] == config.database_name
    assert data['outlier_detection_constant'] == config.outlier_detection_constant
    assert data['timezone'] == str(config.timezone)
    assert data['colors'] == config.colors
