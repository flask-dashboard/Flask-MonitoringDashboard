"""
Tests for the database pruning functionality.
"""
from datetime import datetime, timedelta, timezone

import pytest

from flask_monitoringdashboard.database import (
    Request,
    Outlier,
    StackLine,
    ExceptionOccurrence,
    CodeLine,
)
from flask_monitoringdashboard.core.database_pruning import prune_database_older_than_days


@pytest.mark.parametrize('request_1__time_requested', [datetime.now(timezone.utc) - timedelta(days=60)])
@pytest.mark.parametrize('request_2__time_requested', [datetime.now(timezone.utc) - timedelta(days=10)])
def test_prune_database_older_than_days_deletes_old_requests(session, request_1, request_2):
    """Test that old requests are deleted while recent ones are preserved."""
    # Verify both requests exist before pruning
    assert session.query(Request).filter(Request.id == request_1.id).count() == 1
    assert session.query(Request).filter(Request.id == request_2.id).count() == 1

    # Prune data older than 30 days
    prune_database_older_than_days(30)

    # Refresh session to see changes
    session.expire_all()

    # Old request (60 days) should be deleted
    assert session.query(Request).filter(Request.id == request_1.id).count() == 0
    # Recent request (10 days) should still exist
    assert session.query(Request).filter(Request.id == request_2.id).count() == 1


@pytest.mark.parametrize('request_1__time_requested', [datetime.now(timezone.utc) - timedelta(days=60)])
def test_prune_database_older_than_days_deletes_related_outlier(session, request_1, outlier_1):
    """Test that outliers related to old requests are deleted."""
    # Verify outlier exists
    assert session.query(Outlier).filter(Outlier.id == outlier_1.id).count() == 1

    prune_database_older_than_days(30)
    session.expire_all()

    # Outlier should be deleted along with request
    assert session.query(Outlier).filter(Outlier.id == outlier_1.id).count() == 0


@pytest.mark.parametrize('request_1__time_requested', [datetime.now(timezone.utc) - timedelta(days=60)])
def test_prune_database_older_than_days_deletes_related_stack_lines(session, request_1, stack_line):
    """Test that stack lines related to old requests are deleted."""
    # Verify stack line exists
    assert session.query(StackLine).filter(StackLine.request_id == request_1.id).count() == 1

    prune_database_older_than_days(30)
    session.expire_all()

    # Stack line should be deleted along with request
    assert session.query(StackLine).filter(StackLine.request_id == request_1.id).count() == 0


@pytest.mark.parametrize('request_1__time_requested', [datetime.now(timezone.utc) - timedelta(days=60)])
def test_prune_database_older_than_days_deletes_exception_occurrences(
    session, request_1, exception_occurrence
):
    """Test that exception occurrences related to old requests are deleted."""
    # Verify exception occurrence exists
    assert session.query(ExceptionOccurrence).filter(
        ExceptionOccurrence.id == exception_occurrence.id
    ).count() == 1

    prune_database_older_than_days(30)
    session.expire_all()

    # Exception occurrence should be deleted along with request
    assert session.query(ExceptionOccurrence).filter(
        ExceptionOccurrence.id == exception_occurrence.id
    ).count() == 0


@pytest.mark.parametrize('request_1__time_requested', [datetime.now(timezone.utc) - timedelta(days=365)])
def test_prune_database_older_than_days_very_old_data(session, request_1):
    """Test that very old data (365 days) gets deleted with default retention."""
    request_id = request_1.id
    assert session.query(Request).filter(Request.id == request_id).count() == 1

    prune_database_older_than_days(30)
    session.expire_all()

    # Very old request should be deleted
    assert session.query(Request).filter(Request.id == request_id).count() == 0


@pytest.mark.parametrize('request_1__time_requested', [datetime.now(timezone.utc) - timedelta(days=10)])
def test_prune_database_preserves_recent_data(session, request_1, outlier_1, stack_line):
    """Test that recent data is preserved when pruning."""
    request_id = request_1.id
    outlier_id = outlier_1.id

    # Prune data older than 30 days
    prune_database_older_than_days(30)
    session.expire_all()

    # Everything should still exist since it's only 10 days old
    assert session.query(Request).filter(Request.id == request_id).count() == 1
    assert session.query(Outlier).filter(Outlier.id == outlier_id).count() == 1
    assert session.query(StackLine).filter(StackLine.request_id == request_id).count() == 1
