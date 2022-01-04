from flask_monitoringdashboard.database import User, session_scope, UserQueries
from flask_monitoringdashboard import config


def update_user(new_password, old_password, user_id, user_is_admin):
    with session_scope() as session:
        data_base_operation = UserQueries(session)
        user = data_base_operation.find_by_id(User, user_id)
        user.is_admin = user_is_admin
        if old_password:
            if user.check_password(old_password):
                user.set_password(new_password)
                data_base_operation.finalize_update(user)
                return True
            else:
                return False
        data_base_operation.finalize_update(user)
        return True


def create_default_user(session):
    data_base_operation = UserQueries(session)
    if data_base_operation.count(User) == 0:
        user = User(username=config.username, is_admin=True)
        user.set_password(password=config.password)
        data_base_operation.create_obj(user)


def get_user(username, password):
    """Validates the username and password and returns an User-object if both are valid.
    In case the User-table is empty, a user with default credentials is added.
    """
    with session_scope() as session:
        create_default_user(session)
        database_operation = UserQueries(session)
        user = database_operation.find_one_user_or_none(username=username)
        if user is not None:
            if user.check_password(password=password):
                database_operation.expunge_all()
                return user
    return None


def add_user(username, is_admin, password):
    with session_scope() as session:
        user = User(username=username, is_admin=is_admin)
        user.set_password(password=password)
        data_base_operation = UserQueries(session)
        data_base_operation.create_obj(user)
        data_base_operation.commit()


def delete_user(user_id):
    with session_scope() as session:
        UserQueries(session).delete_user(user_id)


def get_all_users():
    with session_scope() as session:
        users = UserQueries(session).find_all_user()
        return [
            {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
            }
            for user in users
        ]
