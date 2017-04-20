from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms import validators


class LoginForm(Form):
    email = StringField("Email", [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(Form):
    email = StringField("Email", [validators.Email()])
    password = PasswordField("Password", [validators.DataRequired(), validators.Length(min=7),
                                          validators.EqualTo('confirm', message='Password must match')])
    confirm = PasswordField("Confirm password")
    submit = SubmitField("Register")


class QuoteForm(Form):
    quote = StringField("Quote", [validators.DataRequired()])
    submit = SubmitField("Add quote")