from dashboard import blueprint
from flask import redirect, request, session, render_template, url_for
from dashboard.forms import Login
from dashboard.security import secure, check_login, on_logout


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if request.method == 'POST' and form.validate():
        if not check_login(name=form.name.data, password=form.password.data):
            form.name.errors.append('Incorrect username or password')
        else:
            return redirect(url_for('dashboard.index'))
    return render_template('dashboard/login.html', session=session, form=form)


@blueprint.route('/logout')
@secure
def logout():
    return on_logout()
