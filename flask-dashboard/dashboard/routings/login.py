from dashboard import user_app, link, env
from flask import redirect, request, session
from dashboard.forms import Login
from dashboard.security import secure, check_login, on_logout


@user_app.route('/' + link + '/login', methods=['GET', 'POST'])
def dashboard_login():
    form = Login()
    if request.method == 'POST' and form.validate():
        if not check_login(name=form.name.data, password=form.password.data):
            form.name.errors.append('Incorrect username or password')
        else:
            return redirect('/' + link)
    return env.get_template('login.html').render(link=link, session=session, form=form)


@user_app.route('/' + link + '/logout')
@secure
def dashboard_logout():
    return on_logout()
