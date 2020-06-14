from flask_monitoringdashboard import blueprint, config
from flask import redirect, session, render_template, url_for, request, jsonify
from flask_monitoringdashboard.core.auth import on_logout, on_login, secure, is_admin
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.auth import get_user, get_all_users

MAIN_PAGE = config.blueprint_name + '.index'


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

        user = get_user(username=name, password=password)
        if user is not None:
            on_login(admin=user.is_admin)
            return redirect(url_for(MAIN_PAGE))
    return render_template('fmd_login.html', blueprint_name=config.blueprint_name)


@blueprint.route('/logout')
def logout():
    """
    Remove the session variables from the user.
    Redirect the user to the login page.
    :return:
    """
    return on_logout()


@blueprint.route('/api/user_management')
@secure
def user_management():
    """
    :return: A JSON-object with configuration details
    """
    if not is_admin():
        return jsonify([])
    with session_scope() as session:
        return jsonify(get_all_users(session))
