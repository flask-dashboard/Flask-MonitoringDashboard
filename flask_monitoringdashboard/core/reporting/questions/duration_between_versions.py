from flask_monitoringdashboard.core.reporting.answer import Answer
from flask_monitoringdashboard.core.reporting.questions.question import Question
from flask_monitoringdashboard.database import session_scope, Request
from flask_monitoringdashboard.database.request import get_avg_duration_in_time_frame, get_avg_duration


class DurationBetweenVersions(Question):
    def __init__(self, endpoint_id, version1, version2):
        self._endpoint_id = endpoint_id
        self._version1 = version1
        self._version2 = version2

    def answer(self):
        with session_scope() as db_session:
            average_interval_1 = get_avg_duration(db_session, self._endpoint_id,
                                                  Request.version_requested == self._version1)
            average_interval_2 = get_avg_duration_in_time_frame(db_session, self._endpoint_id,
                                                                Request.version_requested == self._version2)

        diff = (average_interval_2 - average_interval_1) / average_interval_1 * 100

        if abs(diff) < 20:  # A 20% change is interesting
            return Answer('', False)

        change = 'decreased' if diff < 0 else 'increased'

        return Answer(f'Latency of endpoint with ID {self._endpoint_id} {change} by {abs(diff)}% ', True)

    def title(self):
        return f'Latency of endpoint {self._endpoint_id}'
