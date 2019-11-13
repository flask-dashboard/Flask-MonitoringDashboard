from collections import defaultdict

from flask_monitoringdashboard.controllers.requests import get_status_code_frequencies_in_interval
from flask_monitoringdashboard.core.reporting.questions.report_question import Answer, ReportQuestion
from flask_monitoringdashboard.database import session_scope


class StatusCodeDistributionAnswer(Answer):
    def __init__(self, is_significant=False, percentages=None):
        super().__init__('STATUS_CODE_DISTRIBUTION')

        self.percentages = percentages
        self._is_significant = is_significant

    def is_significant(self):
        return self._is_significant

    def meta(self):
        return dict(
            percentages=self.percentages
        )


def frequency_to_percentage(freq, total):
    if total == 0:
        raise ValueError('`total` can not be zero!')

    return (float(freq)) / total * 100


class StatusCodeDistribution(ReportQuestion):

    def get_answer(self, endpoint, comparison_interval, compared_to_interval):
        with session_scope() as db_session:
            comparison_interval_frequencies = get_status_code_frequencies_in_interval(db_session, endpoint.id,
                                                                                      comparison_interval.start_date(),
                                                                                      comparison_interval.end_date())


            compared_to_interval_frequencies = get_status_code_frequencies_in_interval(
                db_session, endpoint.id,
                compared_to_interval.start_date(),
                compared_to_interval.end_date())

            registered_status_codes = set(compared_to_interval_frequencies.keys()).union(
                set(comparison_interval_frequencies.keys()))

            total_requests_comparison_interval = sum(comparison_interval_frequencies.values())
            total_requests_compared_to_interval = sum(compared_to_interval_frequencies.values())

            if total_requests_comparison_interval == 0 or total_requests_compared_to_interval == 0:
                return StatusCodeDistributionAnswer(is_significant=False)

            percentages = []
            max_absolute_diff = 0

            for status_code in registered_status_codes:
                count_comparison_interval = comparison_interval_frequencies[
                    status_code] if status_code in comparison_interval_frequencies else 0

                count_compared_to_interval = compared_to_interval_frequencies[
                    status_code] if status_code in compared_to_interval_frequencies else 0

                comparison_interval_percentage = frequency_to_percentage(count_comparison_interval,
                                                                         total_requests_comparison_interval)

                compared_to_interval_percentage = frequency_to_percentage(count_compared_to_interval,
                                                                          total_requests_compared_to_interval)

                percentage_diff = comparison_interval_percentage - compared_to_interval_percentage

                percentages.append(dict(
                    status_code=status_code,
                    comparison_interval=comparison_interval_percentage,
                    compared_to_interval=compared_to_interval_percentage,
                    percentage_diff=percentage_diff
                ))

                max_absolute_diff = max(max_absolute_diff, percentage_diff)

            return StatusCodeDistributionAnswer(is_significant=max_absolute_diff > 3, percentages=percentages)
