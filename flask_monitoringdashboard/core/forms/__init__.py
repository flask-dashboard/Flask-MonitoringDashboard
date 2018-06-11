from flask import request
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField, PasswordField, StringField, SelectField

from .daterange import get_daterange_form
from .double_slider import get_double_slider_form
from .slider import get_slider_form

MONITOR_CHOICES = [
    (0, '0 - Disabled'),
    (1, '1 - Performance'),
    (2, '2 - Profiler'),
    (3, '3 - Profiler + Outliers')]


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
    monitor = SelectField('Monitor', coerce=int, choices=MONITOR_CHOICES)


def get_monitor_form(endpoint, default_value):
    """ Return a form with the endpoint as a variable """
    form = MonitorLevel(request.form)
    form.monitor.default = default_value
    form.monitor.label = endpoint
    form.process()
    return form
