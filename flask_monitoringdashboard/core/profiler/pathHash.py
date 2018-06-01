from flask_monitoringdashboard.core.profiler.stringHash import StringHash

STRING_SPLIT = '->'
LINE_SPLIT = ':'


class PathHash(object):
    """
    Used for encoding the stacktrace.
    A stacktrace can be seen by a list of tuples (filename and linenumber): e.g. [(fn1, 25), (fn2, 30)]
    this is encoded as a string:

        encoded = 'fn1:25->fn2->30'

   However, the filename could possibly contain '->', therefore the filename is hashed into a number.
    So, the encoding becomes:

        encoded = '0:25->1:30'
    """

    def __init__(self):
        self._string_hash = StringHash()
        self._current_path = ''
        self._last_fn = None
        self._last_ln = None

    def set_path(self, path):
        self._current_path = path
        self._last_fn = None
        self._last_ln = None

    def get_path(self, fn, ln):
        """
        :param fn: String with the filename
        :param ln: line number
        :return: Encoded path name.
        """
        if self._last_fn == fn and self._last_ln == ln:
            return self._current_path
        self._last_fn = fn
        self._last_ln = ln
        self._current_path = self.append(fn, ln)
        return self._current_path

    def append(self, fn, ln):
        """
        Concatenate the current_path with the new path.
        :param fn: filename
        :param ln: line number
        :return: The new current_path
        """
        if self._current_path:
            return self._current_path + STRING_SPLIT + self._encode(fn, ln)
        return self._encode(fn, ln)

    def _encode(self, fn, ln):
        return str(self._string_hash.hash(fn)) + LINE_SPLIT + str(ln)

    @staticmethod
    def get_indent(string):
        if string:
            return len(string.split(STRING_SPLIT))
        return 0
