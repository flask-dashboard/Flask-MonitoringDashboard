from flask_monitoringdashboard.core.profiler.stringHash import StringHash

STRING_SPLIT = '->'


class PathHash(object):

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
        if self._current_path:
            return self._current_path + STRING_SPLIT + self._encode(fn, ln)
        return self._encode(fn, ln)

    def _encode(self, fn, ln):
        return str(self._string_hash.hash(fn)) + ':' + str(ln)

    @staticmethod
    def get_indent(string):
        if string:
            return len(string.split(STRING_SPLIT))
        return 0
