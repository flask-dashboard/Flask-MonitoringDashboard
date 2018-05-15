from flask_wtf import FlaskForm
from wtforms import validators, SubmitField, PasswordField, StringField

from .daterange import get_daterange_form
from .double_slider import get_double_slider_form
from .slider import get_slider_form


class Login(FlaskForm):
    """ Used for serving a login form. """
    name = StringField('Username', [validators.data_required()])
    password = PasswordField('Password', [validators.data_required()])
    submit = SubmitField('Login')
