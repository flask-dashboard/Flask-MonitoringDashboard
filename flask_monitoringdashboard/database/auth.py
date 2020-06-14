from flask_monitoringdashboard.database import User, session_scope
from flask_monitoringdashboard import config


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


def get_all_users(session):
    users = session.query(User).order_by(User.id).all()

    return [
        {
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
        }
        for user in users
    ]
