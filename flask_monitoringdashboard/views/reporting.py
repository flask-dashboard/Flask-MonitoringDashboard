from datetime import datetime, timezone

from flask import request, jsonify
from sqlalchemy import and_

from flask_monitoringdashboard.database import Request
from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.date_interval import DateInterval
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard.core.reporting.questions.median_latency import (
    MedianLatency,
)
from flask_monitoringdashboard.core.reporting.questions.status_code_distribution import (
    StatusCodeDistribution,
)
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_endpoints
from flask_monitoringdashboard.database.request import (
    create_time_based_sample_criterion,
)


def get_date(p):
    return datetime.fromtimestamp(int(request.args.get(p)), tz=timezone.utc)


def make_endpoint_summary(endpoint, requests_criterion, baseline_requests_criterion):
    questions = [MedianLatency(), StatusCodeDistribution()]

    summary = dict(
        endpoint_id=endpoint.id,
        endpoint_name=endpoint.name,
        answers=[],
        has_anything_significant=False,
    )

    for question in questions:
        answer = question.get_answer(
            endpoint, requests_criterion, baseline_requests_criterion
        )

        if answer.is_significant():
            summary["has_anything_significant"] = True

        summary["answers"].append(answer.serialize())

    return summary


def make_endpoint_summaries(requests_criterion, baseline_requests_criterion):
    endpoint_summaries = []

    with session_scope() as db_session:
        for endpoint in get_endpoints(db_session):
            endpoint_summary = make_endpoint_summary(
                endpoint, requests_criterion, baseline_requests_criterion
            )
            endpoint_summaries.append(endpoint_summary)

    return dict(summaries=endpoint_summaries)


@blueprint.route("/api/reporting/make_report/intervals", methods=["POST"])
@secure
def make_report_intervals():
    post_to_back_if_telemetry_enabled(**{"name": "reporting/make_reports/intervals"})
    arguments = request.json

    try:
        interval = DateInterval(
            datetime.fromtimestamp(int(arguments["interval"]["from"]), tz=timezone.utc),
            datetime.fromtimestamp(int(arguments["interval"]["to"]), tz=timezone.utc),
        )

        baseline_interval = DateInterval(
            datetime.fromtimestamp(int(arguments["baseline_interval"]["from"]), tz=timezone.utc),
            datetime.fromtimestamp(int(arguments["baseline_interval"]["to"]), tz=timezone.utc),
        )

    except Exception:
        return "Invalid payload", 422

    baseline_requests_criterion = create_time_based_sample_criterion(
        baseline_interval.start_date(), baseline_interval.end_date()
    )
    requests_criterion = create_time_based_sample_criterion(
        interval.start_date(), interval.end_date()
    )

    summaries = make_endpoint_summaries(requests_criterion, baseline_requests_criterion)

    return jsonify(summaries)


@blueprint.route("/api/reporting/make_report/commits", methods=["POST"])
@secure
def make_report_commits():
    post_to_back_if_telemetry_enabled(**{"name": "reporting/make_reports/commits"})
    arguments = request.json

    baseline_commit_version = arguments["baseline_commit_version"]
    commit_version = arguments["commit_version"]

    if None in [baseline_commit_version, commit_version]:
        return dict(message="Please select two commits"), 422

    if baseline_commit_version == commit_version:
        return dict(message="Can't compare commit to itself"), 422

    baseline_requests_criterion = Request.version_requested == baseline_commit_version
    requests_criterion = Request.version_requested == commit_version

    summaries = make_endpoint_summaries(requests_criterion, baseline_requests_criterion)
    return jsonify(summaries)
