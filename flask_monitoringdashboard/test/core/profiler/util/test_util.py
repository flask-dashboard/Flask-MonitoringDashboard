import unittest

from flask_monitoringdashboard.core.profiler.util import order_histogram


class TestProfilerUtil(unittest.TestCase):

    def test_order_histogram(self):
        histogram = {
            ('0:42->1:12', 'c'): 610,
            ('0:42', 'a'): 1234,
            ('0:42->1:13', 'b'): 614
        }
        self.assertEqual(order_histogram(histogram.items()),
                         [(('0:42', 'a'), 1234), (('0:42->1:13', 'b'), 614), (('0:42->1:12', 'c'), 610)])
