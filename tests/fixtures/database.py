import pytest
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.orm import scoped_session

from flask_monitoringdashboard.database import DBSession


@pytest.fixture
def session():
    """Db session."""
    session = scoped_session(DBSession)
    yield session
    session.close()


class ModelFactory(SQLAlchemyModelFactory):
    """Base model factory."""

    class Meta:
        abstract = True
        sqlalchemy_session = scoped_session(DBSession)
        sqlalchemy_session_persistence = 'commit'
