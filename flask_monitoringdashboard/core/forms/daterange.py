import datetime

from flask import request
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField, SelectField
from wtforms.fields.html5 import DateField
import pytz
from flask_monitoringdashboard.database import session_scope, Timezone
from tzlocal import get_localzone


# get local timezone
local_tz = get_localzone()


DATE_FORMAT = '%Y-%m-%d'


def get_tz_default():
    """
    search table Timezone to obtain the timezone info as default timezone
    :return: default timezone
    """
    with session_scope() as db_session:
        tz = db_session.query(Timezone).first()
        if tz is None:
            Timezone.insert_timezone(str(local_tz))
            tz_default = str(local_tz)
        else:
            tz_default = tz.timezone
        return tz_default


class timezone_select_field(SelectField):
    """ Used for selecting timezone to display corresponding time series data """
    def __init__(self, *args, **kwargs):
        super(timezone_select_field, self).__init__(*args, **kwargs)
        self.choices = [(tz, tz) for tz in pytz.common_timezones]
        self.default = get_tz_default()


class SelectDateRangeForm(FlaskForm):
    """ Used for selecting two dates, which together specify a range. """
    start_date = DateField('Start date', format=DATE_FORMAT, validators=[validators.data_required()])
    end_date = DateField('End date', format=DATE_FORMAT, validators=[validators.data_required()])
    timezone = timezone_select_field('Timezone')
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
        tz = form.timezone.data
        Timezone.insert_timezone(tz)
        if form.start_date.data > form.end_date.data:
            form.start_date.data, form.end_date.data = form.end_date.data, form.start_date.data
    else:
        form.end_date.data = datetime.date.today()
        form.start_date.data = form.end_date.data - datetime.timedelta(days=num_days)
    return form
