from flask_monitoringdashboard.controllers.requests import get_status_code_frequencies_in_interval
from flask_monitoringdashboard.core.auth import secure
from datetime import datetime
from flask import request


from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.date_interval import DateInterval
from flask_monitoringdashboard.core.reporting.questions.average_latency import AverageLatency
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_endpoints


def get_date(p) -> datetime:
    return datetime.utcfromtimestamp(int(request.args.get(p)))


def status_code_report(endpoint, comparison_interval, compared_to_interval):
    with session_scope() as db_session:
        comparison_interval_distribution = get_status_code_frequencies_in_interval(db_session, endpoint.id,
                                                                                   comparison_interval.start_date(),
                                                                                   comparison_interval.end_date())

        compared_to_interval_distribution = get_status_code_frequencies_in_interval(db_session, endpoint.id,
                                                                                    compared_to_interval.start_date(),
                                                                                    compared_to_interval.end_date())

        total_requests_comparison_interval = sum(comparison_interval_distribution.values())
        total_requests_compared_to_interval = sum(compared_to_interval_distribution.values())

        percentages_comparison_interval = [(status_code, frequency / total_requests_comparison_interval * 100) for
                                           (status_code, frequency) in
                                           comparison_interval_distribution.items()]

        percentages_compared_to_interval = [(status_code, frequency / total_requests_compared_to_interval * 100) for
                                            (status_code, frequency) in
                                            compared_to_interval_distribution.items()]

        frequencies_comparison_interval = [comparison_interval_distribution[status_code] for status_code in
                                           sorted(comparison_interval_distribution.keys())]

        frequencies_compared_to_interval = [compared_to_interval_distribution[status_code] for status_code in
                                            sorted(compared_to_interval_distribution.keys())]

        chisq, p = 0, 0#chisquare(frequencies_comparison_interval, frequencies_compared_to_interval)

        return dict(
            significant=float(p) < .05,
            percentages_comparison_interval=comparison_interval_distribution,
            percentages_compared_to_interval=percentages_compared_to_interval,
            endpoint=dict(
                id=endpoint.id,
                name=endpoint.name,
            ),
            type='STATUS_CODE_DISTRIBUTION',
        )


def make_endpoint_summary(endpoint, comparison_interval, compared_to_interval):
    questions = [AverageLatency()]

    summary = dict(
        endpoint_id=endpoint.id,
        endpoint_name=endpoint.name,
        answers=[],
        has_anything_significant=False
    )

    for question in questions:
        answer = question.get_answer(endpoint, comparison_interval, compared_to_interval)

        if answer.is_significant():
            summary['has_anything_significant'] = True

        summary['answers'].append(answer.serialize())

    return summary


@blueprint.route('/api/reporting/make_report', methods=['POST'])
@secure
def make_report():
    arguments = request.json

    try:
        comparison_interval = DateInterval(datetime.fromtimestamp(int(arguments['comparison_interval']['from'])),
                                           datetime.fromtimestamp(int(arguments['comparison_interval']['to'])))

        compared_to_interval = DateInterval(datetime.fromtimestamp(int(arguments['compared_to_interval']['from'])),
                                            datetime.fromtimestamp(int(arguments['compared_to_interval']['to'])))

    except Exception as err:
        return 'Invalid payload', 422

    questions = [
        AverageLatency()
    ]

    endpoint_summaries = []
    with session_scope() as db_session:
        for endpoint in get_endpoints(db_session):

            endpoint_summary = make_endpoint_summary(endpoint, comparison_interval, compared_to_interval)
            endpoint_summaries.append(endpoint_summary)

    return dict(
        summaries=endpoint_summaries
    )



    # endpoint_entries = []
    # anything_significant = False
    #
    # with session_scope() as db_session:
    #     for endpoint in get_endpoints(db_session):
    #         comparison_interval_latencies_sample = get_latencies_sample(db_session, endpoint.id, comparison_interval)
    #         compared_to_interval_latencies_sample = get_latencies_sample(db_session, endpoint.id, compared_to_interval)
    #
    #         endpoint_report_entries = [
    #             average_report(endpoint, comparison_interval_latencies_sample, compared_to_interval_latencies_sample),
    #             # status_code_report(endpoint, comparison_interval, compared_to_interval)
    #         ]
    #
    #         has_anything_significant = len(list(filter(lambda k: k['significant'], endpoint_report_entries))) > 0
    #
    #         endpoint_entry = dict(
    #             id=endpoint.id,
    #             name=endpoint.name,
    #             latencies_sample=dict(
    #                 comparison_interval=comparison_interval_latencies_sample,
    #                 compared_to_interval=compared_to_interval_latencies_sample,
    #             ),
    #             entries=endpoint_report_entries,
    #             has_anything_significant=has_anything_significant
    #         )
    #
    #         anything_significant = anything_significant or len(
    #             [entry for entry in endpoint_entry['entries'] if entry['significant']])
    #
    #         endpoint_entries.append(endpoint_entry)
    #
    #     return jsonify(dict(
    #         endpoints=endpoint_entries
    #     ))
