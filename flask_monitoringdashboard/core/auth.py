from functools import wraps
from flask_monitoringdashboard import config
from flask import session, redirect, url_for


def admin_secure(func):
    """
    When the user is not logged into the system, the user is requested to the login page.
    There are two types of user-modes:
    - admin: Can be visited with this wrapper.
    - guest: Cannot be visited with this wrapper.
    :param func: the endpoint to be wrapped.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session and session.get(config.link + '_logged_in'):
            if session.get(config.link + '_admin'):
                return func(*args, **kwargs)
        return redirect(url_for('dashboard.login'))

    return wrapper


def secure(func):
    """
    When the user is not logged into the system, the user is requested to the login page.
    There are two types of user-modes:
    - admin: Can be visited with this wrapper.
    - guest: Can be visited with this wrapper.
    :param func: the endpoint to be wrapped.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session and session.get(config.link + '_logged_in'):
            return func(*args, **kwargs)
        return redirect(url_for('dashboard.login'))

    return wrapper


def is_admin():
    return session and session.get(config.link + '_admin')


def check_login(name, password):
    if name == config.username and password == config.password:
        on_login(admin=True)
        return True
    elif name == config.guest_username and password in config.guest_password:
        on_login(admin=False)
        return True
    return False


def on_login(admin):
    session[config.link + '_logged_in'] = True
    if admin:
        session[config.link + '_admin'] = True


def on_logout():
    session.pop(config.link + '_logged_in', None)
    session.pop(config.link + '_admin', None)
    return redirect(url_for('dashboard.login'))
