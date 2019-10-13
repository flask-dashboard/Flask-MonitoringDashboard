class DateInterval(object):
    def __init__(self, start_date, end_date):
        if start_date > end_date:
            raise ValueError('start_date must be before or equals to end_date')

        self._start_date = start_date
        self._end_date = end_date

    def start_date(self):
        return self._start_date

    def end_date(self):
        return self._end_date

    def __repr__(self):
        return str((self._start_date, self._end_date))
