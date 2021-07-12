import flask
from flask import redirect, render_template, url_for, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.auth import on_logout, on_login, secure, is_admin, admin_secure
from flask_monitoringdashboard.database import session_scope, User
from flask_monitoringdashboard.database.auth import get_user, get_all_users

MAIN_PAGE = config.blueprint_name + '.index'
BAD_REQUEST_STATUS = 400


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    User for logging into the system. The POST-request checks whether the logging is valid.
    If this is the case, the user is redirected to the main page.
    :return:
    """
    if flask.session.get(config.link + '_logged_in'):
        return redirect(url_for(MAIN_PAGE))

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = get_user(username=name, password=password)
        if user is not None:
            on_login(user=user)
            return redirect(url_for(MAIN_PAGE))
    return render_template('fmd_login.html', 
        blueprint_name=config.blueprint_name, 
        show_login_banner=config.show_login_banner, 
        show_login_footer=config.show_login_footer,
    )


@blueprint.route('/logout')
def logout():
    """
    Remove the session variables from the user.
    Redirect the user to the login page.
    :return:
    """
    return on_logout()


@blueprint.route('/api/users')
@secure
def users_list():
    """
    :return: A JSON-object with configuration details
    """
    if not is_admin():
        return jsonify([])
    with session_scope() as session:
        return jsonify(get_all_users(session))


@blueprint.route('/api/user/delete', methods=['POST'])
@admin_secure
def user_delete():
    """Delete the user in the database."""
    user_id = int(request.form['user_id'])
    if flask.session.get(config.link + '_user_id') == user_id:
        return jsonify({'message': 'Cannot delete itself.'}), BAD_REQUEST_STATUS
    with session_scope() as session:
        session.query(User).filter(User.id == user_id).delete()
    return 'OK'


@blueprint.route('/api/user/create', methods=['POST'])
@admin_secure
def user_create():
    """Create a new user, and save in the database."""
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    is_admin = request.form['is_admin'] == 'true'

    if password != password2:
        return jsonify({'message': "Passwords don't match."}), BAD_REQUEST_STATUS

    with session_scope() as session:
        try:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password=password)
            session.add(user)
            session.commit()
        except IntegrityError:
            return jsonify({'message': "Username already exists."}), BAD_REQUEST_STATUS
        except Exception as e:
            return jsonify({'message': str(e)}), BAD_REQUEST_STATUS
    return 'OK'


@blueprint.route('/api/user/edit', methods=['POST'])
@admin_secure
def user_edit():
    """Update the user in the database."""
    user_id = int(request.form['user_id'])
    is_admin = request.form['is_admin'] == 'true'
    if flask.session.get(config.link + '_user_id') == user_id and not is_admin:
        return jsonify({'message': 'Cannot remove the admin permissions from itself.'}), BAD_REQUEST_STATUS

    with session_scope() as session:
        try:
            user = session.query(User).filter(User.id == user_id).one()
            user.is_admin = is_admin

            old_password = request.form.get('old_password')
            if old_password is not None:
                if user.check_password(old_password):
                    new_password = request.form['new_password']
                    new_password2 = request.form['new_password2']

                    if new_password != new_password2:
                        return jsonify({'message': "Passwords don't match."}), BAD_REQUEST_STATUS

                    user.set_password(new_password)
                else:
                    return jsonify({'message': "Old password doesn't match."}), BAD_REQUEST_STATUS
        except NoResultFound:
            return jsonify({'message': "User ID doesn't exist."}), BAD_REQUEST_STATUS
        except Exception as e:
            return jsonify({'message': str(e)}), BAD_REQUEST_STATUS
    return 'OK'
