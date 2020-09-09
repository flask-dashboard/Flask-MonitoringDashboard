import uuid

import pytest

from flask_monitoringdashboard.database import User

BAD_REQUEST = 400


@pytest.mark.parametrize('user__is_admin', [False])
def test_users_guest(dashboard_user):
    response = dashboard_user.get('dashboard/api/users')
    assert response.status_code == 200
    assert response.json == []


def test_users_admin(dashboard_user, user):
    response = dashboard_user.get('dashboard/api/users')
    assert response.status_code == 200
    [row] = [row for row in response.json if row['id'] == user.id]
    assert row == {'id': user.id, 'username': user.username, 'is_admin': user.is_admin}


def test_user_delete_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/user/delete')
    assert not response.is_json


@pytest.mark.parametrize('user__is_admin', [False])
def test_user_delete_admin_secure(dashboard_user, another_user):
    """Not allowed if the user is a guest user. Therefore, it should redirect."""
    response = dashboard_user.post(
        'dashboard/api/user/delete',
        data={'user_id': another_user.id},
    )
    assert response.status_code == 302
    assert b'Redirecting' in response.data


def test_user_delete_normal_flow(dashboard_user, another_user, session):
    response = dashboard_user.post(
        'dashboard/api/user/delete',
        data={'user_id': another_user.id},
    )
    assert response.status_code == 200
    assert response.data == b'OK'
    assert session.query(User).filter(User.username == another_user.username).count() == 0


def test_user_delete_cannot_delete_itself(dashboard_user, user, session):
    response = dashboard_user.post(
        'dashboard/api/user/delete',
        data={'user_id': user.id},
    )
    assert response.status_code == BAD_REQUEST
    assert response.json['message'] == 'Cannot delete itself.'


def test_user_create_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/user/create')
    assert not response.is_json


@pytest.mark.parametrize('user__is_admin', [False])
def test_user_create_admin_secure(dashboard_user):
    """Not allowed if the user is a guest user. Therefore, it should redirect."""
    response = dashboard_user.post('dashboard/api/user/create')
    assert response.status_code == 302
    assert b'Redirecting' in response.data


def test_user_create_passwords_different(dashboard_user, another_user):
    response = dashboard_user.post('dashboard/api/user/create', data={
        'username': another_user.username,
        'password': another_user.password,
        'password2': another_user.password + 'abc',
        'is_admin': 'true'
    })
    assert response.status_code == BAD_REQUEST
    assert response.json['message'] == "Passwords don't match."


def test_user_create_username_exists(dashboard_user, another_user):
    response = dashboard_user.post('dashboard/api/user/create', data={
        'username': another_user.username,
        'password': another_user.password,
        'password2': another_user.password,
        'is_admin': 'true'
    })
    assert response.status_code == BAD_REQUEST
    assert response.json['message'] == "Username already exists."


@pytest.mark.parametrize('is_admin', [True, False])
def test_user_create_success(dashboard_user, session, is_admin):
    username = str(uuid.uuid4())
    password = str(uuid.uuid4())
    response = dashboard_user.post('dashboard/api/user/create', data={
        'username': username,
        'password': password,
        'password2': password,
        'is_admin': 'true' if is_admin else 'false',
    })
    assert response.status_code == 200
    assert response.data == b'OK'

    user = session.query(User).filter(User.username == username).one()
    assert user.check_password(password)
    assert user.is_admin is is_admin


def test_user_edit_get(dashboard_user):
    """GET is not allowed. It should return the overview page."""
    response = dashboard_user.get('dashboard/api/user/edit')
    assert not response.is_json


@pytest.mark.parametrize('user__is_admin', [False])
def test_user_edit_admin_secure(dashboard_user):
    """Not allowed if the user is a guest user. Therefore, it should redirect."""
    response = dashboard_user.post('dashboard/api/user/edit')
    assert response.status_code == 302
    assert b'Redirecting' in response.data


def test_user_edit_user_id_does_not_exists(dashboard_user, session):
    new_user_id = session.query(User).count() + 1
    response = dashboard_user.post('dashboard/api/user/edit', data={
        'user_id': new_user_id,
        'is_admin': 'true',
    })
    assert response.status_code == BAD_REQUEST
    assert response.json['message'] == "User ID doesn't exist."


def test_user_edit_passwords_dont_match(dashboard_user, another_user):
    response = dashboard_user.post('dashboard/api/user/edit', data={
        'user_id': another_user.id,
        'old_password': another_user.password,
        'new_password': 'abc',
        'new_password2': 'abcd',
        'is_admin': 'true',
    })
    assert response.status_code == BAD_REQUEST
    assert response.json['message'] == "Passwords don't match."


def test_user_edit_old_password_does_not_match(dashboard_user, another_user):
    response = dashboard_user.post('dashboard/api/user/edit', data={
        'user_id': another_user.id,
        'old_password': another_user.password + 'abc',
        'is_admin': 'true',
    })
    assert response.status_code == BAD_REQUEST
    assert response.json['message'] == "Old password doesn't match."


@pytest.mark.parametrize('another_user__is_admin', [False])
def test_user_edit_update_is_admin_only(dashboard_user, another_user, session):
    response = dashboard_user.post('dashboard/api/user/edit', data={
        'user_id': another_user.id,
        'is_admin': 'true',
    })
    assert response.status_code == 200
    assert response.data == b'OK'

    # reload the user
    user = session.query(User).filter(User.id == another_user.id).one()
    assert user.is_admin is True


@pytest.mark.parametrize('another_user__is_admin', [False])
def test_user_edit_update_password(dashboard_user, another_user, session):
    new_password = 'abc'
    response = dashboard_user.post('dashboard/api/user/edit', data={
        'user_id': another_user.id,
        'old_password': another_user.password,
        'new_password': new_password,
        'new_password2': new_password,
        'is_admin': 'true',
    })
    assert response.status_code == 200
    assert response.data == b'OK'

    # reload the user
    user = session.query(User).filter(User.id == another_user.id).one()
    assert user.is_admin is True
    assert user.check_password(new_password) is True
