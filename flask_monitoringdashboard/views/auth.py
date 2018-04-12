from flask_monitoringdashboard import blueprint, config
from flask import redirect, request, session, render_template, url_for
from flask_monitoringdashboard.forms import Login
from flask_monitoringdashboard.security import check_login, on_logout


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

    form = Login()
    if request.method == 'POST' and form.validate():
        if not check_login(name=form.name.data, password=form.password.data):
            form.name.errors.append('Incorrect username or password')
        else:
            return redirect(url_for(MAIN_PAGE))
    return render_template('login.html', form=form)


@blueprint.route('/logout')
def logout():
    return on_logout()
