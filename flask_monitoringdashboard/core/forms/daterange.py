import datetime

from flask import request
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField
from wtforms.fields.html5 import DateField

DATE_FORMAT = '%Y-%m-%d'


class SelectDateRangeForm(FlaskForm):
    """ Used for selecting two dates, which together specify a range. """
    start_date = DateField('Start date', format=DATE_FORMAT, validators=[validators.data_required()])
    end_date = DateField('End date', format=DATE_FORMAT, validators=[validators.data_required()])
    submit = SubmitField('Submit')
    type = 'SelectDateRangeForm'

    def get_days(self):
        """
        :return: A list with datetime.date object from form.start_date to (including) form.end_date
        """
        delta = self.end_date.data - self.start_date.data
        return [self.start_date.data + datetime.timedelta(days=i) for i in range(delta.days + 1)]


def get_daterange_form(num_days=20):
    """
    Returns a SelectDateRangeForm with two dates:
    - end_date is today
    - start_date is the today - numdays
    :param num_days: the date for the start_date
    :return: A SelectDateRangeForm object with the required logic
    """
    form = SelectDateRangeForm(request.form)
    if form.validate():
        if form.start_date.data > form.end_date.data:
            form.start_date.data, form.end_date.data = form.end_date.data, form.start_date.data
    else:
        form.end_date.data = datetime.date.today()
        form.start_date.data = form.end_date.data - datetime.timedelta(days=num_days)
    return form
