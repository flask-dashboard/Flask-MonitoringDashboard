def test_static_css(dashboard):
    response = dashboard.get('dashboard/static/css/main.css')
    assert response.status_code == 200


def test_static_js(dashboard):
    response = dashboard.get('dashboard/static/js/app.js')
    assert response.status_code == 200
