from flask import request
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField, PasswordField, StringField, SelectField

from .daterange import get_daterange_form
from .double_slider import get_double_slider_form
from .slider import get_slider_form

MONITOR_CHOICES = [
    (0, '0 - Nothing'),
    (1, '1 - Performance'),
    (2, '2 - Outliers'),
    (3, '3 - All requests')]


class Login(FlaskForm):
    """ Used for serving a login form. """
    name = StringField('Username', [validators.data_required()])
    password = PasswordField('Password', [validators.data_required()])
    submit = SubmitField('Login')


class RunTests(FlaskForm):
    """ Used for serving a login form on /{{ link }}/testmonitor. """
    submit = SubmitField('Run selected tests')


class MonitorLevel(FlaskForm):
    """ Used in the Rules page (per endpoint)"""
    monitor = SelectField('Monitor', choices=MONITOR_CHOICES)


def get_monitor_form(endpoint):
    """ Return a form with the endpoint as a variable """
    form = MonitorLevel(request.form)
    form.endpoint = endpoint
    return form
