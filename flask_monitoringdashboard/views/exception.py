from flask import jsonify

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard.controllers.exceptions import (
    get_function_definition_code,
    get_exception_groups,
    get_exception_groups_with_details_for_endpoint,
    get_exception_group_page_number_for_endpoint,
)
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.database.exception_occurrence import (
    count_grouped_exceptions,
    count_endpoint_grouped_exceptions,
    delete_exception_group,
)


@blueprint.route("/api/exception_occurrence/<int:offset>/<int:per_page>")
@secure
def get_exception_occurrence(offset: int, per_page: int):
    """
    Get information about all the exceptions that have occured for all endpoint
    :return: A JSON-list with a JSON-object per exception-group (grouped by endpoint and stack trace)
    """
    post_to_back_if_telemetry_enabled(**{"name": "exception_occurrence"})
    with session_scope() as session:
        exceptions = get_exception_groups(session, offset, per_page)

        return jsonify(exceptions)


@blueprint.route("/api/num_exceptions")
@secure
def num_exceptions():
    post_to_back_if_telemetry_enabled(**{"name": f"num_exceptions"})
    with session_scope() as session:
        return jsonify(count_grouped_exceptions(session))


@blueprint.route("/api/num_exceptions/<int:endpoint_id>")
@secure
def num_endpoint_exceptions(endpoint_id: int):
    post_to_back_if_telemetry_enabled(**{"name": f"num_endpoint_exceptions"})
    with session_scope() as session:
        return jsonify(count_endpoint_grouped_exceptions(session, endpoint_id))


@blueprint.route(
    "/api/detailed_exception_occurrence/<int:endpoint_id>/<int:offset>/<int:per_page>"
)
@secure
def get_detailed_exception_occurrence_endpoint(endpoint_id: int, offset: int, per_page: int):
    """
    Get information about all the exceptions that have occured for a specific endpoint
    :return: A JSON-list with a JSON-object per stacktrace snapshot id
    """
    post_to_back_if_telemetry_enabled(**{"name": "detailed_exception_occurrence"})
    with session_scope() as session:
        exceptions = get_exception_groups_with_details_for_endpoint(
            session, offset, per_page, endpoint_id
        )

        return jsonify(exceptions)


@blueprint.route(
    "/api/exception_occurrence_page_number/<int:endpoint_id>/<int:stack_trace_snapshot_id>/<int:per_page>"
)
@secure
def get_exception_occurrence_endpoint_page_number(endpoint_id: int, stack_trace_snapshot_id: int, per_page: int):
    """
    Get the page number of an exception group that has occurred for a specific endpoint
    :return: The page number of the exception group (int)
    """
    post_to_back_if_telemetry_enabled(**{"name": "exception_occurrence_page_number"})
    with session_scope() as session:
        result = get_exception_group_page_number_for_endpoint(session, per_page, endpoint_id, stack_trace_snapshot_id)
        return jsonify(result)


@blueprint.route("/api/function_code/<int:function_definition_id>")
@secure
def get_function_code(function_definition_id):
    """
    Get the function code for a specific function involved in an exception.
    :return: The function's source code (str)
    """
    post_to_back_if_telemetry_enabled(**{"name": "function_code"})
    with session_scope() as session:
        definition = get_function_definition_code(session, function_definition_id)
        return jsonify(definition)


@blueprint.route(
    "/api/exception_occurrence/<int:stack_trace_snapshot_id>", methods=["DELETE"]
)
@secure
def delete_exception(stack_trace_snapshot_id: int):
    post_to_back_if_telemetry_enabled(**{"name": "delete_exception"})
    with session_scope() as session:
        delete_exception_group(session, stack_trace_snapshot_id)
    return "ok"
