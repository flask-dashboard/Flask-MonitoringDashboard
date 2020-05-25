from flask_monitoringdashboard.core.profiler.util import order_histogram


def test_order_histogram():
    histogram = {('0:42->1:12', 'c'): 610, ('0:42', 'a'): 1234, ('0:42->1:13', 'b'): 614}
    assert order_histogram(histogram.items()) == (
        [(('0:42', 'a'), 1234), (('0:42->1:13', 'b'), 614), (('0:42->1:12', 'c'), 610)]
    )
