import numpy as np
from scipy.stats import median_test

from flask_monitoringdashboard.core.reporting.questions.report_question import (
    ReportAnswer,
    ReportQuestion,
)
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.request import get_latencies_sample


class MedianLatencyReportAnswer(ReportAnswer):
    def __init__(
            self,
            is_significant,
            latencies_sample=None,
            baseline_latencies_sample=None,
            percentual_diff=None,
            median=None,
            baseline_median=None,
    ):
        super().__init__('MEDIAN_LATENCY')

        self._is_significant = is_significant

        self._baseline_latencies_sample = baseline_latencies_sample
        self._latencies_sample = latencies_sample

        self._percentual_diff = percentual_diff

        self._baseline_median = baseline_median
        self._median = median

    def meta(self):
        return dict(
            latencies_samples=dict(
                baseline=self._baseline_latencies_sample,
                comparison=self._latencies_sample
            ),
            median=self._median,
            baseline_median=self._baseline_median,
            percentual_diff=self._percentual_diff,
        )

    def is_significant(self):
        return self._is_significant


class MedianLatency(ReportQuestion):
    def get_answer(self, endpoint, requests_criterion, baseline_requests_criterion):
        with session_scope() as session:
            latencies_sample = get_latencies_sample(session, endpoint.id,
                                                    requests_criterion)
            baseline_latencies_sample = get_latencies_sample(
                session, endpoint.id, baseline_requests_criterion
            )

            if len(latencies_sample) == 0 or len(baseline_latencies_sample) == 0:
                return MedianLatencyReportAnswer(
                    is_significant=False,
                    latencies_sample=latencies_sample,
                    baseline_latencies_sample=baseline_latencies_sample,
                )

            median = float(np.median(latencies_sample))
            baseline_median = float(np.median(baseline_latencies_sample))

            percentual_diff = (median - baseline_median) / baseline_median * 100

            _, p, _, _ = median_test(latencies_sample, baseline_latencies_sample)

            is_significant = abs(float(percentual_diff)) > 0 and float(p) < 0.05

            return MedianLatencyReportAnswer(
                is_significant=is_significant,
                percentual_diff=percentual_diff,
                # Sample latencies
                latencies_sample=latencies_sample,
                baseline_latencies_sample=baseline_latencies_sample,
                # Latency medians
                median=median,
                baseline_median=baseline_median,
            )
