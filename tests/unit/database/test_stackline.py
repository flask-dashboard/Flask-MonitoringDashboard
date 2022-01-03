from flask_monitoringdashboard.database.stack_line import (
    add_stack_line,
    get_profiled_requests,
    get_grouped_profiled_requests,
)

from flask_monitoringdashboard.database import StackLine


def test_add_stackline(session, request_1):
    if getattr(StackLine, "is_mongo_db", False):
        assert StackLine().get_collection(session).find_one({"request_id": request_1.id}) is None
    else:
        assert session.query(StackLine).filter(StackLine.request_id == request_1.id).one_or_none() is None
    add_stack_line(session, request_id=request_1.id, position=0, indent=1, duration=1, code_line="code")
    if not getattr(StackLine, "is_mongo_db", False):
        session.commit()
        assert session.query(StackLine).filter(StackLine.request_id == request_1.id).one()
    else:
        assert StackLine().get_collection(session).find_one({"request_id": request_1.id}) is not None


def test_get_profiled_requests(session, endpoint, request_1):
    assert not get_profiled_requests(session, endpoint_id=endpoint.id, offset=0, per_page=10)
    add_stack_line(session, request_id=request_1.id, position=0, indent=1, duration=1, code_line="code")
    if not getattr(StackLine, "is_mongo_db", False):
        session.commit()
    assert get_profiled_requests(session, endpoint_id=endpoint.id, offset=0, per_page=10)


def test_get_grouped_profiled_requests(session, request_1, endpoint):
    assert not get_grouped_profiled_requests(session, endpoint_id=endpoint.id)
    add_stack_line(session, request_id=request_1.id, position=0, indent=1, duration=1, code_line="code")
    if not getattr(StackLine, "is_mongo_db", False):
        session.commit()
    assert get_grouped_profiled_requests(session, endpoint_id=endpoint.id)
