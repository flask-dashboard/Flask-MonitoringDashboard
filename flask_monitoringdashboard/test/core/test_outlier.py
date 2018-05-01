import time
import unittest


class TestOutlier(unittest.TestCase):

    def test_stackinfo(self):
        """
            One test for all outlier functionality
        """
        from flask_monitoringdashboard.core.outlier import StackInfo
        stack_info = StackInfo(average=1)
        time.sleep(0.01)
        stack_info.stop()
        self.assertIsNotNone(stack_info.stacktrace)
        self.assertIsNotNone(stack_info.cpu_percent)
        self.assertIsNotNone(stack_info.memory)
