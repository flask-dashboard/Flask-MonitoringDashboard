from flask_monitoringdashboard import blueprint, config
from flask import redirect, session, render_template, url_for, request
from flask_monitoringdashboard.core.auth import on_logout, on_login

MAIN_PAGE = 'dashboard.index'


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    User for logging into the system. The POST-request checks whether the logging is valid.
    If this is the case, the user is redirected to the main page.
    :return:
    """
    if session.get(config.link + '_logged_in'):
        return redirect(url_for(MAIN_PAGE))

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        if name == config.username and password == config.password:
            on_login(admin=True)
            return redirect(url_for(MAIN_PAGE))
        elif name == config.guest_username and password in config.guest_password:
            on_login(admin=False)
            return redirect(url_for(MAIN_PAGE))

    return render_template('fmd_login.html')


@blueprint.route('/logout')
def logout():
    """
    Remove the session variables from the user.
    Redirect the user to the login page.
    :return:
    """
    return on_logout()
