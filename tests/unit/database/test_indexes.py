"""
Tests for create_missing_indexes in flask_monitoringdashboard/database/__init__.py.
"""
from sqlalchemy import inspect

from flask_monitoringdashboard.database import Request, create_missing_indexes, engine


def _request_index_names():
    return {ix["name"] for ix in inspect(engine).get_indexes(Request.__tablename__)}


def test_create_missing_indexes_adds_index_to_existing_table():
    index = next(ix for ix in Request.__table__.indexes if "time" in ix.name)
    index.drop(engine)
    assert index.name not in _request_index_names()

    create_missing_indexes(engine)

    assert index.name in _request_index_names()


def test_create_missing_indexes_is_idempotent():
    before = _request_index_names()
    create_missing_indexes(engine)
    assert _request_index_names() == before
