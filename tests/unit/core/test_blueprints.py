import pytest

from flask_monitoringdashboard.core.blueprints import get_blueprint


@pytest.mark.parametrize('name', ['Fiddler'])
def test_get_blueprint(name):
    actual = get_blueprint(name)
    assert actual == 'Fiddler'


@pytest.mark.parametrize('name', ['Anomander.Purake'])
def test_get_blueprint_double_gives_first(name):
    actual = get_blueprint(name)
    assert actual == 'Anomander'


@pytest.mark.parametrize('name', ['Karsa.Orlong.Toblakai'])
def test_get_blueprint_triple_gives_first(name):
    actual = get_blueprint(name)
    assert actual == 'Karsa'


@pytest.mark.usefixtures('request_context')
@pytest.mark.parametrize('name', [''])
def test_get_blueprint_blank_gives_blank(name):
    actual = get_blueprint(name)
    assert actual == ''
