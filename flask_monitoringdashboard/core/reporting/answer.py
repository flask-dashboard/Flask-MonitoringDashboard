from abc import abstractmethod


class Answer(object):
    def __init__(self, is_interesting):
        self._is_interesting = is_interesting

    def is_interesting(self):
        return self._is_interesting



    @abstractmethod
    def to_markdown(self):
        raise NotImplementedError()
