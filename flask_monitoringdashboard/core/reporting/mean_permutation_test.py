from __future__ import division
import numpy as np


def mean_diff(x, y):
    return np.abs(np.mean(x) - np.mean(y))


def mean_permutation_test(x, y, num_rounds=1000):
    """
    Performs a non-parametric test to check whether `x` and `y` come from the same distribution.

    :param x: a sample from some distribution
    :param y: a sample to compare x to
    :param num_rounds: number of different permutations to test. Increase this number to increase
     the accuracy
    :return: The p-value
    """
    rng = np.random.RandomState()

    m = len(x)
    combined = np.hstack((x, y))

    more_extreme = 0
    reference_stat = mean_diff(x, y)

    for i in range(num_rounds):
        rng.shuffle(combined)

        if mean_diff(combined[:m], combined[m:]) > reference_stat:
            more_extreme += 1

    return more_extreme / num_rounds
