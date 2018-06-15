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

    def set_path(self, path):
        self._current_path = path

    def get_path(self, fn, ln):
        """
        :param fn: String with the filename
        :param ln: line number
        :return: Encoded path name.
        """
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
        """
        Encoded fn and ln in the following way:
            _encode(fn, ln) => hash(fn):ln
        :param fn: filename (string)
        :param ln: linenumber (int)
        :return: String with the hashed filename, and linenumber
        """

        return str(self._string_hash.hash(fn)) + LINE_SPLIT + str(ln)

    def _decode(self, string):
        """ Opposite of _encode

        Example: _decode('0:12') => ('fn1', 12)
        """
        hash, ln = string.split(LINE_SPLIT)
        return self._string_hash.unhash(int(hash)), int(ln)

    @staticmethod
    def get_indent(path):
        """
        Compute the amount of callers given a path.
        :param path: the path from the root to the statement
        :return: an integer
        """
        if path:
            return len(path.split(STRING_SPLIT))
        return 0

    def get_code(self, path):
        """
        :param path: only take the last tuple of the path. the last part contains the code line, but hashed.
        :return: the line of code, based on the given path
        """
        last = path.rpartition(STRING_SPLIT)[-1]
        return self._string_hash.unhash(int(last.split(LINE_SPLIT, 1)[1]))

    def get_last_fn_ln(self, string):
        last = string.rpartition(STRING_SPLIT)[-1]
        return self._decode(last)

    def get_stacklines_path(self, stack_lines, index):
        """
        Used for grouping multiple requests
        :param stack_lines: list of StackLine objects.
        :param index: index in the stack_lines, so 0 <= index < len(stack_lines)
        :return: the StackLinePath that belongs to the given index
        """
        self.set_path('')
        path = []
        while index >= 0:
            path.append(stack_lines[index].code)
            current_indent = stack_lines[index].indent
            while index >= 0 and stack_lines[index].indent != current_indent - 1:
                index -= 1
        for code_line in reversed(path):
            self._current_path = self.append(code_line.filename, self._string_hash.hash(code_line.code))
        return self._current_path
