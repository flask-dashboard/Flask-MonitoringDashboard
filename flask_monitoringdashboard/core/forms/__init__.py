from flask_wtf import FlaskForm
from wtforms import validators, SubmitField, PasswordField, StringField
from .daterange import get_daterange_form
from .slider import get_slider_form


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
