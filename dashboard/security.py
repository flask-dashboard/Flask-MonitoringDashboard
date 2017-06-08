from functools import wraps
from dashboard import user_app, config
from dashboard.database.settings import get_setting
from flask import session, redirect, url_for


def secure(func):
    """
        Whenever the application is run in debug mode, no login is required
        When a login is required, the user is requested to the login page, 
        if he is not logged in
    :param func: the function to be secured
    :return: 
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if user_app.debug or (session and session.get(config.link + '_logged_in')):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('dashboard.login'))
    return wrapper


def check_login(name, password):
    if name == get_setting('username', 'admin') and password == get_setting('password', 'admin'):
        on_login()
        return True
    return False


def on_login():
    session[config.link + '_logged_in'] = True


def on_logout():
    session.pop(config.link + '_logged_in', None)
    return redirect(url_for('dashboard.index'))
