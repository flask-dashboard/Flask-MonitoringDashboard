from flask_monitoringdashboard.core.profiler.util.stringHash import StringHash

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

    def get_path(self, fn, ln, text=''):
        """
        :param fn: String with the filename
        :param ln: line number
        :param text: String with the text on the given line.
        :return: Encoded path name.
        """
        if self._last_fn == fn and self._last_ln == ln:
            return self._current_path
        self._last_fn = fn
        self._last_ln = ln
        self._current_path = self.append(fn, ln, text)
        return self._current_path

    def append(self, fn, ln, text=''):
        """
        Concatenate the current_path with the new path.
        :param fn: filename
        :param ln: line number
        :param text: String with the text on the given line.
        :return: The new current_path
        """
        if self._current_path:
            return self._current_path + STRING_SPLIT + self._encode(fn, ln, text)
        return self._encode(fn, ln, text)

    def _encode(self, fn, ln, text):
        return str(self._string_hash.hash(fn)) + LINE_SPLIT + str(ln) + LINE_SPLIT + text

    def _decode(self, string):
        """ Opposite of _encode

        Example: _decode('0:12') => ('fn1', 12)
        """
        hash, ln, _ = string.split(LINE_SPLIT)
        return self._string_hash.unhash(int(hash)), int(ln)

    @staticmethod
    def get_indent(string):
        if string:
            return len(string.split(STRING_SPLIT))
        return 0

    def get_code(self, path):
        last = path.rpartition(STRING_SPLIT)[-1]
        return last.split(LINE_SPLIT, 2)[2]

    def get_last_fn_ln(self, string):
        last = string.rpartition(STRING_SPLIT)[-1]
        return self._decode(last)

    def get_stacklines_path(self, stack_lines, index):
        self.set_path('')
        path = []
        while index >= 0:
            path.append(stack_lines[index].code)
            current_indent = stack_lines[index].indent
            while index >= 0 and stack_lines[index].indent != current_indent - 1:
                index -= 1
        for code_line in reversed(path):
            self._current_path = self.append(code_line.filename, code_line.line_number, code_line.code)
        return self._current_path
