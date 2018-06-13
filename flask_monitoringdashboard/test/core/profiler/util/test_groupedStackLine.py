import unittest
from math import sqrt


class TestGroupedStackLine(unittest.TestCase):

    def test_grouped_stackline(self):
        from flask_monitoringdashboard.core.profiler.util.groupedStackLine import GroupedStackLine
        grouped_stackline = GroupedStackLine(indent=0, code='code', values=[10, 10, 40], total_sum=100, total_hits=6)
        self.assertEqual(grouped_stackline.hits, 3)
        self.assertEqual(grouped_stackline.sum, 60)
        self.assertEqual(grouped_stackline.standard_deviation, sqrt(200))
        self.assertEqual(grouped_stackline.hits_percentage, .5)
        self.assertEqual(grouped_stackline.percentage, .6)
        self.assertEqual(grouped_stackline.average, 20)