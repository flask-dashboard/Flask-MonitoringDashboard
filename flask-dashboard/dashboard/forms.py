from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import SubmitField, PasswordField, StringField


class MonitorDashboard(FlaskForm):
    """ Used for selecting a number of checkboxes that corresponds to which endpoints should be followed. 
    Since the number of checkboxes is variable (equals the number of endpoints), none of them is added as
    a field to this class. In fact, they are generated in the template in plain html. """
    submit = SubmitField('Save changes')


class Login(FlaskForm):
    """ Used for serving a login form on /{{ link}}/login. """
    name = StringField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
    submit = SubmitField('Login')


class ChangeSetting(FlaskForm):
    """ Used for changing the username of password that is required to login on the dashboard. """
    username = StringField('Username', [validators.required()])
    password = PasswordField('New password', [validators.equal_to(fieldname='confirm')])
    confirm = PasswordField('Confirm password')
    submit = SubmitField('Update changes')
