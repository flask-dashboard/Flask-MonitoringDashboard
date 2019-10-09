from __future__ import division
from numpy import std


class GroupedStackLine(object):
    def __init__(self, indent, code, values, total_sum, total_hits):
        self.indent = indent
        self.code = code
        self.values = values
        self.total_sum = total_sum
        self.total_hits = total_hits
        self.index = 0

    @property
    def hits(self):
        return len(self.values)

    @property
    def sum(self):
        return sum(self.values)

    @property
    def standard_deviation(self):
        return std(self.values)

    @property
    def hits_percentage(self):
        return self.hits / self.total_hits

    @property
    def percentage(self):
        return self.sum / self.total_sum

    @property
    def average(self):
        return self.sum / self.hits
