from flask_monitoringdashboard.core.reporting.mean_permutation_test import mean_permutation_test
import numpy as np

from flask_monitoringdashboard.core.reporting.questions.report_question import Answer, ReportQuestion
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.database.request import get_latencies_sample


class AverageLatencyAnswer(Answer):
    def __init__(self, is_significant, comparison_interval_latencies_sample=None,
                 compared_to_interval_latencies_sample=None, percentual_diff=None, comparison_interval_avg=None,
                 compared_to_interval_avg=None):
        super().__init__('AVERAGE_LATENCY')

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


class AverageLatency(ReportQuestion):

    def get_answer(self, endpoint, comparison_interval, compared_to_interval):
        with session_scope() as db_session:
            comparison_interval_latencies_sample = get_latencies_sample(db_session, endpoint.id, comparison_interval)
            compared_to_interval_latencies_sample = get_latencies_sample(db_session, endpoint.id, compared_to_interval)

            if len(comparison_interval_latencies_sample) == 0 or len(compared_to_interval_latencies_sample) == 0:
                return AverageLatencyAnswer(is_significant=False)

            comparison_interval_avg = np.average(comparison_interval_latencies_sample)
            compared_to_interval_avg = np.average(compared_to_interval_latencies_sample)

            percentual_diff = (comparison_interval_avg - compared_to_interval_avg) / compared_to_interval_avg * 100

            p_value = mean_permutation_test(comparison_interval_latencies_sample,
                                            compared_to_interval_latencies_sample,
                                            num_rounds=1000)
            is_significant = abs(float(percentual_diff)) > 30 and p_value < 0.05

            return AverageLatencyAnswer(
                is_significant=is_significant,

                percentual_diff=percentual_diff,

                # Sample latencies
                comparison_interval_latencies_sample=comparison_interval_latencies_sample,
                compared_to_interval_latencies_sample=compared_to_interval_latencies_sample,

                # Latency averages
                comparison_interval_avg=comparison_interval_avg,
                compared_to_interval_avg=compared_to_interval_avg
            )
