from flask_monitoringdashboard.views.details.profiler import get_body


class GroupedStackLine(object):

    def __init__(self, indent, code, hits, sum, total):
        self.indent = indent
        self.code = code
        self.hits = hits
        self.sum = sum
        self.total = total
        self.body = []

    def compute_body(self, index, table):
        self.body = get_body(index, table)

    @property
    def percentage(self):
        return self.sum / self.total

    @property
    def average(self):
        return self.total / self.hits

