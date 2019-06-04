from flask_monitoringdashboard.controllers.requests import get_status_code_frequencies_in_interval
from flask_monitoringdashboard.core.reporting.answer import Answer
from flask_monitoringdashboard.core.reporting.date_interval import DateInterval
from flask_monitoringdashboard.core.reporting.questions.question import Question
from flask_monitoringdashboard.database import session_scope, Request
from scipy.stats import chisquare


class ErrorStatusCodesBetweenIntervalsAnswer(Answer):

    def __init__(self, is_interesting, distribution_interval_1, distribution_interval_2):
        super().__init__(is_interesting)

        self._distribution_interval_1 = distribution_interval_1
        self._distribution_interval_2 = distribution_interval_2

    def to_markdown(self):
        print(self._distribution_interval_1)

        total_requests_interval_1 = sum(self._distribution_interval_1.values())
        total_requests_interval_2 = sum(self._distribution_interval_2.values())

        print(total_requests_interval_1)
        print(total_requests_interval_2)

        percentages_interval_1 = [(status_code, frequency / total_requests_interval_1 * 100) for
                                  (status_code, frequency) in
                                  self._distribution_interval_1.items()]

        percentages_interval_2 = [(status_code, frequency / total_requests_interval_1 * 100) for
                                  (status_code, frequency) in
                                  self._distribution_interval_2.items()]

        print(percentages_interval_1)
        print(percentages_interval_2)

        COLUMN_WIDTH = 15

        lines = [
            ''.join(['Status Code'.ljust(COLUMN_WIDTH), 'Old'.ljust(COLUMN_WIDTH), 'New'.ljust(COLUMN_WIDTH),
                     'Diff'.ljust(COLUMN_WIDTH)])
        ]

        for ((status_code, percentage), (_, percentage_2)) in zip(percentages_interval_1, percentages_interval_2):
            print(status_code, percentage, percentage_2)

            p1 = round(percentage, 1)
            p2 = round(percentage_2, 1)

            diff = round(percentage_2 - percentage, 1)

            lines.append(''.join([
                str(status_code).ljust(COLUMN_WIDTH),
                (str(p1) + '%').ljust(COLUMN_WIDTH),
                (str(p2) + '%').ljust(COLUMN_WIDTH),
                (str(diff) + '%').ljust(COLUMN_WIDTH),
            ]))

        return '\n'.join(lines)


class ErrorStatusCodesBetweenIntervals(Question):

    def __init__(self, endpoint_id, interval1: DateInterval, interval2: DateInterval):
        self._endpoint_id = endpoint_id
        self._interval1 = interval1
        self._interval2 = interval2

    def answer(self):
        with session_scope() as db_session:
            distribution_interval_1 = get_status_code_frequencies_in_interval(db_session, self._endpoint_id,
                                                                              self._interval1.start_date(),
                                                                              self._interval1.end_date())

            distribution_interval_2 = get_status_code_frequencies_in_interval(db_session, self._endpoint_id,
                                                                              self._interval2.start_date(),
                                                                              self._interval2.end_date())

            frequencies_interval_1 = [distribution_interval_1[status_code] for status_code in
                                      sorted(distribution_interval_1.keys())]

            frequencies_interval_2 = [distribution_interval_2[status_code] for status_code in
                                      sorted(distribution_interval_2.keys())]

            chisq, p = chisquare(frequencies_interval_1, frequencies_interval_2)

            return ErrorStatusCodesBetweenIntervalsAnswer(p < 0.05, distribution_interval_1, distribution_interval_2)
