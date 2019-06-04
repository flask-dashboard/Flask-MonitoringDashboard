from flask_monitoringdashboard.core.reporting.answer import Answer
from flask_monitoringdashboard.core.reporting.date_interval import DateInterval
from flask_monitoringdashboard.core.reporting.questions.question import Question
from flask_monitoringdashboard.database import session_scope, Request
from flask_monitoringdashboard.database.request import get_avg_duration_in_time_frame, get_avg_duration


class DurationBetweenIntervalsAnswer(Answer):

    def __init__(self, is_interesting, result):
        super().__init__(is_interesting)
        self._result = result

    def to_markdown(self):
        return self._result


class DurationBetweenIntervals(Question):
    def answer(self) -> Answer:
        with session_scope() as db_session:
            average_interval_1 = get_avg_duration_in_time_frame(db_session, self._endpoint_id,
                                                                self._interval1.start_date(),
                                                                self._interval1.end_date())
            average_interval_2 = get_avg_duration_in_time_frame(db_session, self._endpoint_id,
                                                                self._interval2.start_date(),
                                                                self._interval2.end_date())

        diff = (average_interval_2 - average_interval_1) / average_interval_1 * 100

        if abs(diff) < 20:  # A 20% change is interesting
            return Answer('', False)

        change = 'decreased' if diff < 0 else 'increased'

        return DurationBetweenIntervalsAnswer(True,
                                              f'Latency of endpoint with ID {self._endpoint_id} {change} by {abs(diff)}% ', )

    def title(self):
        return f'Latency of endpoint {self._endpoint_id}'

    def __init__(self, endpoint_id, interval1: DateInterval, interval2: DateInterval):
        self._endpoint_id = endpoint_id
        self._interval1 = interval1
        self._interval2 = interval2
