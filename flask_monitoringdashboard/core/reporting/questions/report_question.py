from abc import ABCMeta, abstractmethod


class ReportAnswer:
    __metaclass__ = ABCMeta

    def __init__(self, type):
        self.type = type

    @abstractmethod
    def is_significant(self):
        pass

    @abstractmethod
    def meta(self):
        """
        Should return a `dict` that contains any additional information required on the
        frontend. This will be included in the response.
        """
        pass

    def serialize(self):
        base = dict(is_significant=self.is_significant(), type=self.type)
        base.update(self.meta())

        return base


class ReportQuestion:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_answer(self, endpoint, requests_criterion, baseline_requests_criterion):
        pass
