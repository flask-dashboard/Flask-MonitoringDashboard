import numpy as np


def mean_diff(x, y):
    return np.abs(np.mean(x) - np.mean(y))


def mean_permutation_test(x, y, num_rounds=1000):
    """


    :param x:
    :param y:
    :param num_rounds:
    :return:
    """
    rng = np.random.RandomState()

    m, n = len(x), len(y)
    combined = np.hstack((x, y))

    more_extreme = 0
    reference_stat = mean_diff(x, y)

    for i in range(num_rounds):
        rng.shuffle(combined)
        if mean_diff(combined[:m], combined[m:]) > reference_stat:
            more_extreme += 1

    return more_extreme / num_rounds
