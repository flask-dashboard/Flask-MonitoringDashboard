from flask_monitoringdashboard.controllers.requests import \
    get_status_code_frequencies_in_interval
from flask_monitoringdashboard.core.reporting.questions.report_question import (
    ReportAnswer,
    ReportQuestion,
)
from flask_monitoringdashboard.database import session_scope


class StatusCodeDistributionReportAnswer(ReportAnswer):
    def __init__(self, is_significant=False, percentages=None):
        super().__init__('STATUS_CODE_DISTRIBUTION')

        self.percentages = percentages
        self._is_significant = is_significant

    def is_significant(self):
        return self._is_significant

    def meta(self):
        return dict(percentages=self.percentages)


def frequency_to_percentage(freq, total):
    if total == 0:
        raise ValueError('`total` can not be zero!')

    return (float(freq)) / total * 100


class StatusCodeDistribution(ReportQuestion):
    MIN_NUM_REQUESTS = 30
    MIN_PERCENTAGE_DIFF_THRESHOLD = 3

    def get_answer(self, endpoint, requests_criterion, baseline_requests_criterion):

        with session_scope() as session:

            frequencies = get_status_code_frequencies_in_interval(session, endpoint.id,
                                                                  requests_criterion)

            baseline_frequencies = get_status_code_frequencies_in_interval(
                session,
                endpoint.id,
                baseline_requests_criterion
            )

        # all monitored status codes in both intervals
        all_monitored_status_codes = set(baseline_frequencies.keys()).union(
            set(frequencies.keys()))

        total_requests = sum(frequencies.values())
        total_baseline_requests = sum(baseline_frequencies.values())

        if (
            total_requests < self.MIN_NUM_REQUESTS
            or total_baseline_requests < self.MIN_NUM_REQUESTS
        ):
            return StatusCodeDistributionReportAnswer(is_significant=False)

        percentages = []
        max_percentage_diff = 0

        for status_code in all_monitored_status_codes:
            count = frequencies[status_code] if status_code in frequencies else 0

            baseline_count = (
                baseline_frequencies[status_code] if status_code in baseline_frequencies else 0
            )

            percentage = frequency_to_percentage(freq=count, total=total_requests)
            baseline_percentage = frequency_to_percentage(
                freq=baseline_count, total=total_baseline_requests
            )

            percentage_diff = percentage - baseline_percentage

            percentages.append(
                dict(
                    status_code=status_code,
                    comparison=percentage,
                    baseline=baseline_percentage,
                    percentage_diff=percentage_diff,
                )
            )

            max_percentage_diff = max(max_percentage_diff, percentage_diff)

        return StatusCodeDistributionReportAnswer(
            is_significant=max_percentage_diff > self.MIN_PERCENTAGE_DIFF_THRESHOLD,
            percentages=percentages,
        )
