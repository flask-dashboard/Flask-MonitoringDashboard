from flask_monitoringdashboard.core.reporting.questions.question import Question, Answer
import numpy as np
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.database.request import get_latencies_sample


def stolen_permutation_test(x, y, func='x_mean != y_mean', method='exact', num_rounds=1000, seed=None):
    """
    Nonparametric permutation test

    Parameters
    -------------
    x : list or numpy array with shape (n_datapoints,)
        A list or 1D numpy array of the first sample
        (e.g., the treatment group).
    y : list or numpy array with shape (n_datapoints,)
        A list or 1D numpy array of the second sample
        (e.g., the control group).
    func : custom function or str (default: 'x_mean != y_mean')
        function to compute the statistic for the permutation test.
        - If 'x_mean != y_mean', uses
          `func=lambda x, y: np.abs(np.mean(x) - np.mean(y)))`
           for a two-sided test.
        - If 'x_mean > y_mean', uses
          `func=lambda x, y: np.mean(x) - np.mean(y))`
           for a one-sided test.
        - If 'x_mean < y_mean', uses
          `func=lambda x, y: np.mean(y) - np.mean(x))`
           for a one-sided test.
    method : 'approximate' or 'exact' (default: 'exact')
        If 'exact' (default), all possible permutations are considered.
        If 'approximate' the number of drawn samples is
        given by `num_rounds`.
        Note that 'exact' is typically not feasible unless the dataset
        size is relatively small.
    num_rounds : int (default: 1000)
        The number of permutation samples if `method='approximate'`.
    seed : int or None (default: None)
        The random seed for generating permutation samples if
        `method='approximate'`.

    Returns
    ----------
    p-value under the null hypothesis

    Examples
    -----------
    For usage examples, please see
    http://rasbt.github.io/mlxtend/user_guide/evaluate/permutation_test/

    """

    if method not in ('approximate', 'exact'):
        raise AttributeError('method must be "approximate"'
                             ' or "exact", got %s' % method)

    if isinstance(func, str):

        if func not in (
                'x_mean != y_mean', 'x_mean > y_mean', 'x_mean < y_mean'):
            raise AttributeError('Provide a custom function'
                                 ' lambda x,y: ... or a string'
                                 ' in ("x_mean != y_mean", '
                                 '"x_mean > y_mean", "x_mean < y_mean")')

        elif func == 'x_mean != y_mean':
            def func(x, y):
                return np.abs(np.mean(x) - np.mean(y))

        elif func == 'x_mean > y_mean':
            def func(x, y):
                return np.mean(x) - np.mean(y)

        else:
            def func(x, y):
                return np.mean(y) - np.mean(x)

    rng = np.random.RandomState(seed)

    m, n = len(x), len(y)
    combined = np.hstack((x, y))

    more_extreme = 0.
    reference_stat = func(x, y)

    # Note that whether we compute the combinations or permutations
    # does not affect the results, since the number of permutations
    # n_A specific objects in A and n_B specific objects in B is the
    # same for all combinations in x_1, ... x_{n_A} and
    # x_{n_{A+1}}, ... x_{n_A + n_B}
    # In other words, for any given number of combinations, we get
    # n_A! x n_B! times as many permutations; hoewever, the computed
    # value of those permutations that are merely re-arranged combinations
    # does not change. Hence, the result, since we divide by the number of
    # combinations or permutations is the same, the permutations simply have
    # "n_A! x n_B!" as a scaling factor in the numerator and denominator
    # and using combinations instead of permutations simply saves computational
    # time

    for i in range(num_rounds):
        rng.shuffle(combined)
        if func(combined[:m], combined[m:]) > reference_stat:
            more_extreme += 1.

    return more_extreme / num_rounds


class AverageLatencyAnswer(Answer):
    def __init__(self, _endpoint, is_significant, comparison_interval_latencies_sample,
                 compared_to_interval_latencies_sample, percentual_diff=None, comparison_interval_avg=None,
                 compared_to_interval_avg=None):
        super().__init__('AVERAGE_LATENCY')

        self._endpoint = _endpoint
        self._is_significant = is_significant
        self._comparison_interval_latencies_sample = comparison_interval_latencies_sample
        self._compared_to_interval_latencies_sample = compared_to_interval_latencies_sample
        self._percentual_diff = percentual_diff

        self._compared_to_interval_avg = compared_to_interval_avg
        self._comparison_interval_avg = comparison_interval_avg

    def meta(self):
        return dict(
            latencies_sample=dict(
                comparison_interval=self._comparison_interval_latencies_sample,
                compared_to_interval=self._compared_to_interval_latencies_sample
            ),
            comparison_average=self._comparison_interval_avg,
            compared_to_average=self._compared_to_interval_avg,
            percentual_diff=self._percentual_diff,
        )

    def is_significant(self):
        return self._is_significant


class AverageLatency(Question):

    def get_answer(self, endpoint, comparison_interval, compared_to_interval):
        with session_scope() as db_session:
            comparison_interval_latencies_sample = get_latencies_sample(db_session, endpoint.id, comparison_interval)
            compared_to_interval_latencies_sample = get_latencies_sample(db_session, endpoint.id, compared_to_interval)

            if len(comparison_interval_latencies_sample) == 0 or len(compared_to_interval_latencies_sample) == 0:
                return AverageLatencyAnswer(endpoint, False, comparison_interval_latencies_sample,
                                            compared_to_interval_latencies_sample)

            comparison_interval_avg = np.average(comparison_interval_latencies_sample)
            compared_to_interval_avg = np.average(compared_to_interval_latencies_sample)

            percentual_diff = (comparison_interval_avg - compared_to_interval_avg) / compared_to_interval_avg * 100

            p_value = stolen_permutation_test(comparison_interval_latencies_sample,
                                              compared_to_interval_latencies_sample,
                                              func='x_mean != y_mean',
                                              method='approximate',
                                              num_rounds=1000,
                                              seed=0)

            is_significant = abs(float(percentual_diff)) > 30 and p_value < 0.05

            return AverageLatencyAnswer(endpoint, is_significant, comparison_interval_latencies_sample,
                                        compared_to_interval_latencies_sample, percentual_diff, comparison_interval_avg,
                                        compared_to_interval_avg)
