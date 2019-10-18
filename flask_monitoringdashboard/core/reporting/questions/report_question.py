
from abc import ABCMeta, abstractmethod


class Answer:
    __metaclass__ = ABCMeta

    def __init__(self, type):
        self.type = type

    @abstractmethod
    def is_significant(self):
        pass

    @abstractmethod
    def meta(self):
        pass

    def serialize(self):
        base = dict(
            is_significant=self.is_significant(),
            type=self.type
        )
        base.update(self.meta())

        return base


class ReportQuestion:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_answer(self, endpoint, comparison_interval, compared_to_interval):
        pass
