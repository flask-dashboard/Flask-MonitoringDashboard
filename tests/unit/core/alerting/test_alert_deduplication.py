"""
Tests that an alert is sent once per kind of exception, not once per occurrence.
(Corresponding to the files: 'core/alerting/fingerprint.py', 'database/alert_fingerprint.py'
and the alerting part of 'core/exceptions/exception_collector.py')
"""

from unittest.mock import patch

import pytest

from flask_monitoringdashboard.core.alerting.fingerprint import alert_fingerprint
from flask_monitoringdashboard.core.exceptions.exception_collector import ExceptionCollector
from flask_monitoringdashboard.database import AlertFingerprint
from flask_monitoringdashboard.database.alert_fingerprint import claim_alert_fingerprint


def _raise_from_source(source, message, filename="app/views.py"):
    """Defines f() from source and returns the exception it raises, as if app code had raised it."""
    namespace = {}
    exec(compile(source, filename, "exec"), namespace)
    try:
        namespace["f"](message)
    except Exception as e:
        return e


def _not_found(user_id):
    raise KeyError(f"user {user_id} not found")


def _bad_input(value):
    raise ValueError(f"bad input {value}")


def _caught(fn, *args):
    try:
        fn(*args)
    except Exception as e:
        return e


F = "def f(msg):\n    raise ValueError(msg)\n"
F_EDITED = "import os\n\n\ndef f(msg):\n    x = 1\n    raise ValueError(msg)\n"
G = "def g(msg):\n    raise ValueError(msg)\n\ndef f(msg):\n    g(msg)\n"


def _fp(e):
    return alert_fingerprint(e, e.__traceback__)


def test_fingerprint_ignores_the_message():
    assert _fp(_raise_from_source(F, "user 1 not found")) == _fp(_raise_from_source(F, "user 2 not found"))


def test_fingerprint_ignores_line_numbers_and_function_edits():
    assert _fp(_raise_from_source(F, "a")) == _fp(_raise_from_source(F_EDITED, "a"))


def test_fingerprint_distinguishes_the_call_path():
    assert _fp(_raise_from_source(F, "a")) != _fp(_raise_from_source(G, "a"))


def test_fingerprint_distinguishes_the_file():
    assert _fp(_raise_from_source(F, "a")) != _fp(_raise_from_source(F, "a", filename="app/other.py"))


def test_fingerprint_distinguishes_the_exception_type():
    other_type = F.replace("ValueError", "TypeError")
    assert _fp(_raise_from_source(F, "a")) != _fp(_raise_from_source(other_type, "a"))


def _forget(session, fingerprint):
    session.query(AlertFingerprint).filter_by(hash=fingerprint).delete()
    session.commit()


def test_claim_succeeds_only_once(session):
    fingerprint = "test-claim-fingerprint"
    _forget(session, fingerprint)

    assert claim_alert_fingerprint(fingerprint) is True
    assert claim_alert_fingerprint(fingerprint) is False


@pytest.fixture
def alerting_config():
    from flask_monitoringdashboard import config

    config.alert_enabled = True
    yield config
    config.alert_enabled = False


def _collector_with(*exceptions):
    collector = ExceptionCollector()
    for e in exceptions:
        collector.add_user_captured_exc(e)
    return collector


def test_repeated_exception_alerts_once(session, request_1, alerting_config):
    first = _caught(_not_found, 1)
    _forget(session, _fp(first))

    with patch("flask_monitoringdashboard.core.exceptions.exception_collector.send_alert") as send_alert:
        _collector_with(first).save_to_db(request_1.id, session, alerting_config)
        _collector_with(_caught(_not_found, 2)).save_to_db(request_1.id, session, alerting_config)

    assert send_alert.call_count == 1


def test_no_alert_when_alerting_disabled(session, request_1):
    from flask_monitoringdashboard import config

    e = _caught(_not_found, 3)
    _forget(session, _fp(e))

    with patch("flask_monitoringdashboard.core.exceptions.exception_collector.send_alert") as send_alert:
        _collector_with(e).save_to_db(request_1.id, session, config)

    send_alert.assert_not_called()


def test_failing_alert_does_not_stop_saving(session, request_1, alerting_config):
    from flask_monitoringdashboard.database import ExceptionOccurrence

    first, second = _caught(_not_found, 4), _caught(_bad_input, 5)
    _forget(session, _fp(first))
    before = session.query(ExceptionOccurrence).filter_by(request_id=request_1.id).count()

    with patch(
        "flask_monitoringdashboard.core.exceptions.exception_collector.send_alert",
        side_effect=RuntimeError("smtp down"),
    ):
        _collector_with(first, second).save_to_db(request_1.id, session, alerting_config)

    assert session.query(ExceptionOccurrence).filter_by(request_id=request_1.id).count() == before + 2
