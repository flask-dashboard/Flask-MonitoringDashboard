import unittest
import numpy as np
from flask_monitoringdashboard.core.reporting.mean_permutation_test import mean_permutation_test


class TestMeanPermutationTest(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)  # We want tests to be deterministic

    def test_different_random_distributions(self):
        x = np.random.randint(0, 16, 100)  # 100 random numbers between 0 and 16
        y = np.random.randint(0, 10, 100)  # 100 random numbers between 0 and 10

        p = mean_permutation_test(x, y)

        self.assertLess(
            p, 0.05
        )  # p < 0.05 -> reject null hypothesis that distributions come from same distribution

    def test_different_normal_distributions(self):
        x = np.random.normal(5, 10, 100)  # mu=5, sd=10
        y = np.random.normal(0, 10, 100)  # mu=0, sd=10

        p = mean_permutation_test(x, y)

        self.assertLess(
            p, 0.05
        )  # p < 0.05 -> reject null hypothesis that distributions come from same distribution

    def test_equal_normal_distributions(self):
        x = np.random.normal(0, 10, 100)  # mu=0, sd=10
        y = np.random.normal(0, 10, 100)  # ditto

        p = mean_permutation_test(x, y)

        self.assertGreater(p, 0.05)

    def test_equal_random_distributions(self):
        x = np.random.randint(0, 10, 100)  # 100 random numbers between 0 and 10
        y = np.random.randint(0, 10, 100)  # ditto

        p = mean_permutation_test(x, y)

        self.assertGreater(p, 0.05)
