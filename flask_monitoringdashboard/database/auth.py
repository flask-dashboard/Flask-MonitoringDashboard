from flask_monitoringdashboard.database import DatabaseConnectionWrapper
from flask_monitoringdashboard import config


def update_user(new_password, old_password, user_id, user_is_admin):
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        data_base_operation = database_connection_wrapper.database_connection.user_queries(session)
        user = data_base_operation.find_by_id(database_connection_wrapper.database_connection.user, user_id)
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
    database_connection_wrapper = DatabaseConnectionWrapper()
    data_base_operation = database_connection_wrapper.database_connection.user_queries(session)
    if data_base_operation.count(database_connection_wrapper.database_connection.user) == 0:
        user = database_connection_wrapper.database_connection.user(username=config.username, is_admin=True)
        user.set_password(password=config.password)
        data_base_operation.create_obj(user)


def get_user(username, password):
    """Validates the username and password and returns an User-object if both are valid.
    In case the User-table is empty, a user with default credentials is added.
    """
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        create_default_user(session)
        database_operation = database_connection_wrapper.database_connection.user_queries(session)
        user = database_operation.find_one_user_or_none(username=username)
        if user is not None:
            if user.check_password(password=password):
                database_operation.expunge_all()
                return user
    return None


def add_user(username, is_admin, password):
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        user = database_connection_wrapper.database_connection.user(username=username, is_admin=is_admin)
        user.set_password(password=password)
        data_base_operation = database_connection_wrapper.database_connection.user_queries(session)
        data_base_operation.create_obj(user)
        data_base_operation.commit()


def delete_user(user_id):
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        database_connection_wrapper.database_connection.user_queries(session).delete_user(user_id)


def get_all_users():
    database_connection_wrapper = DatabaseConnectionWrapper()
    with database_connection_wrapper.database_connection.session_scope() as session:
        users = database_connection_wrapper.database_connection.user_queries(session).find_all_user()
        return [
            {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
            }
            for user in users
        ]
