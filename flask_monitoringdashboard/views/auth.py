from flask_monitoringdashboard import blueprint, config
from flask import redirect, request, session, render_template, url_for
from flask_monitoringdashboard.forms import Login
from flask_monitoringdashboard.security import check_login, on_logout


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if session.get(config.link + '_logged_in'):
        return redirect(url_for('dashboard.index'))

    form = Login()
    if request.method == 'POST' and form.validate():
        if not check_login(name=form.name.data, password=form.password.data):
            form.name.errors.append('Incorrect username or password')
        else:
            return redirect(url_for('dashboard.index'))
    return render_template('dashboard/login.html', session=session, form=form)


@blueprint.route('/logout')
def logout():
    return on_logout()
