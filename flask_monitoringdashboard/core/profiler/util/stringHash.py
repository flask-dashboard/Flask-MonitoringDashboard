"""
Class used for hashing the paths.
"""


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

    def unhash(self, hash):
        """ Opposite of hash.

        unhash(hash('abc')) == 'abc

        :param hash: string to be unhashed
        :return: the value that corresponds to the given hash
        """

        for k, v in self._h.items():
            if v == hash:
                return k

        raise ValueError('Value not possible to unhash: {}'.format(hash))
