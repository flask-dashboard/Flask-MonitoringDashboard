from flask_monitoringdashboard.core.reporting.answer import Answer
from abc import ABC, abstractmethod


class Question(ABC):

    @abstractmethod
    def answer(self):
        raise NotImplementedError()
