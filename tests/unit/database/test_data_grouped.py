from flask_monitoringdashboard.database.data_grouped import (
    get_endpoint_data_grouped,
    get_version_data_grouped,
)


def test_get_endpoint_data_grouped(session, request_1):
    data = get_endpoint_data_grouped(session, lambda x: x)
    for key, value in data:
        if key == request_1.endpoint_id:
            assert value == [request_1.duration]
            return
    assert False, "Shouldn't reach here."


def test_get_version_data_grouped(session, request_1):
    data = get_version_data_grouped(session, lambda x: x)
    for key, value in data:
        if key == request_1.version_requested:
            assert value == [request_1.duration]
            return
    assert False, "Shouldn't reach here."
