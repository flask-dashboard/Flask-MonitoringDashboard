

class StringHash(object):

    def __init__(self):
        self._h = {}

    def hash(self, string):
        """
        Performs the following reduction:

        hash('abc') ==> 0
        hash('def') ==> 1
        hash('abc') ==> 0

        :param string: the string to be hashed
        :return: a unique int for every string.
        """
        if string in self._h:
            return self._h[string]
        self._h[string] = len(self._h)
        return self._h[string]
