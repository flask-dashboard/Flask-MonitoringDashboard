from flask_monitoringdashboard.database import User, session_scope
from flask_monitoringdashboard import config


def update_user(new_password, old_password, user_id, user_is_admin):
    with session_scope() as session:
        user = session.query(User).filter(User.id == user_id).one()
        user.is_admin = user_is_admin
        if old_password:
            if user.check_password(old_password):
                user.set_password(new_password)
                return True
            else:
                return False
        return True


def get_user(username, password):
    """Validates the username and password and returns an User-object if both are valid.
    In case the User-table is empty, a user with default credentials is added.
    """
    with session_scope() as session:
        if session.query(User).count() == 0:
            user = User(username=config.username, is_admin=True)
            user.set_password(password=config.password)
            session.add(user)

        user = session.query(User).filter(User.username == username).one_or_none()
        if user is not None:
            if user.check_password(password=password):
                session.expunge_all()
                return user

    return None


def add_user(username, is_admin, password):
    with session_scope() as session:
        user = User(username=username, is_admin=is_admin)
        user.set_password(password=password)
        session.add(user)
        session.commit()


def delete_user(user_id):
    with session_scope() as session:
        session.query(User).filter(User.id == user_id).delete()


def get_all_users():
    with session_scope() as session:
        users = session.query(User).order_by(User.id).all()

        return [
            {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
            }
            for user in users
        ]
