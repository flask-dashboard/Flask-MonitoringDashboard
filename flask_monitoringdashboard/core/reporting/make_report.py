from flask_monitoringdashboard.core.reporting.date_interval import DateInterval
from flask_monitoringdashboard.core.reporting.questions.duration_between_intervals import DurationBetweenIntervals
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_endpoints


class Report(object):
    _questions_and_answers = []

    def add_question_and_answer(self, question, answer):
        self._questions_and_answers.append((question, answer))

    def questions_and_answers(self):
        return self._questions_and_answers


def markdown_serialize_report(report):
    md = ""

    for (question, answer) in report.questions_and_answers():
        md += '# ' + question.title() + '\n'
        md += answer.get_text() + '\n'
        md += '\n'

    return md


def make_report(a: DateInterval, b: DateInterval):
    questions = []

    with session_scope() as db_session:
        endpoints = get_endpoints(db_session)

        for endpoint in endpoints:
            questions.append(DurationBetweenIntervals(endpoint.id, a, b))

    md = ''

    for question in questions:
        answer = question.answer()

        if answer.is_interesting():
            md += answer.to_markdown() + '\n'




