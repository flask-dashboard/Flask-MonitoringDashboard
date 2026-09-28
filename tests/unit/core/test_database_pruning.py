"""
Tests for flask_monitoringdashboard/core/database_pruning.py
"""
from datetime import datetime, timedelta, timezone

from flask_monitoringdashboard.core.database_pruning import prune_database_older_than_weeks
from flask_monitoringdashboard.database import (
    ExceptionOccurrence,
    Outlier,
    Request,
    StackLine,
)
from tests.fixtures.database import ModelFactory
from tests.fixtures.models import (
    OutlierFactory,
    RequestFactory,
    StackLineFactory,
)


def _request_with_children(time_requested):
    request = RequestFactory(time_requested=time_requested)
    OutlierFactory(request=request)
    StackLineFactory(request=request)
    session = ModelFactory._meta.sqlalchemy_session
    session.add(
        ExceptionOccurrence(
            request_id=request.id,
            exception_type_id=1,
            exception_msg_id=1,
            stack_trace_snapshot_id=1,
            is_user_captured=False,
        )
    )
    session.commit()
    return request.id


def _rows_for(session, model, request_ids):
    return session.query(model).filter(model.request_id.in_(request_ids)).count()


def test_prune_deletes_old_requests_and_their_children_in_batches(session):
    now = datetime.now(timezone.utc)
    old_ids = [_request_with_children(now - timedelta(weeks=10)) for _ in range(5)]
    recent_id = _request_with_children(now - timedelta(days=1))

    # batch_size 2 over 5 old requests: two full batches and a partial one
    prune_database_older_than_weeks(4, delete_custom_graph_data=False, batch_size=2)
    session.expire_all()

    assert session.query(Request).filter(Request.id.in_(old_ids)).count() == 0
    for model in (Outlier, StackLine, ExceptionOccurrence):
        assert _rows_for(session, model, old_ids) == 0

    assert session.query(Request).filter(Request.id == recent_id).count() == 1
    for model in (Outlier, StackLine, ExceptionOccurrence):
        assert _rows_for(session, model, [recent_id]) == 1


def test_prune_with_nothing_to_delete(session):
    recent_id = _request_with_children(datetime.now(timezone.utc))

    prune_database_older_than_weeks(4, delete_custom_graph_data=False, batch_size=2)
    session.expire_all()

    assert session.query(Request).filter(Request.id == recent_id).count() == 1
