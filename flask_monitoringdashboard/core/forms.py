import datetime

from flask import request
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField, PasswordField, StringField
from wtforms.fields.html5 import DateField

DATE_FORMAT = '%Y-%m-%d'


class MonitorDashboard(FlaskForm):
    """ Used for selecting a number of checkboxes that corresponds to which endpoints should be followed. 
    Since the number of checkboxes is variable (equals the number of endpoints), none of them is added as
    a field to this class. In fact, they are generated in the template in plain html. """


class Login(FlaskForm):
    """ Used for serving a login form. """
    name = StringField('Username', [validators.data_required()])
    password = PasswordField('Password', [validators.data_required()])
    submit = SubmitField('Login')


class RunTests(FlaskForm):
    """ Used for serving a login form on /{{ link }}/testmonitor. """
    submit = SubmitField('Run selected tests')


class SelectDateRangeForm(FlaskForm):
    """ Used for selecting two dates, which together specify a range. """
    start_date = DateField('Start date', format=DATE_FORMAT, validators=[validators.required()])
    end_date = DateField('End date', format=DATE_FORMAT, validators=[validators.required()])
    submit = SubmitField('Submit')


def get_daterange_form():
    """
    :return: A SelectDateRangeForm object with the required logic
    """
    form = SelectDateRangeForm(request.form)
    if form.validate():
        if form.start_date.data > form.end_date.data:
            form.start_date.data, form.end_date.data = form.end_date.data, form.start_date.data
    else:
        form.end_date.data = datetime.date.today()
        form.start_date.data = form.end_date.data - datetime.timedelta(days=20)
    return form
