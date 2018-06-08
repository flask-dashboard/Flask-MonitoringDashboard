from flask_monitoringdashboard.views.details.profiler import get_body


class GroupedStackLine(object):

    def __init__(self, indent, code, values, total):
        self.indent = indent
        self.code = code
        self.values = values
        self.total = total
        self.body = []
        self.index = 0

    def compute_body(self, index, table):
        self.index = index
        self.body = get_body(index, table)

    @property
    def hits(self):
        return len(self.values)

    @property
    def sum(self):
        return sum(self.values)

    @property
    def percentage(self):
        return self.sum / self.total

    @property
    def average(self):
        return self.sum / self.hits

