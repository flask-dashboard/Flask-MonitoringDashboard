from flask_monitoringdashboard.database import DatabaseConnectionWrapper
from flask_monitoringdashboard.database.auth import get_user


database_connection_wrapper = DatabaseConnectionWrapper()


User = database_connection_wrapper.database_connection.user
UserQueries = database_connection_wrapper.database_connection.user_queries


def test_get_user_adds_default(session, config):
    # delete all existing users
    UserQueries(session).delete_all_users()
    UserQueries(session).commit()
    new_user = get_user(config.username, config.password)
    assert UserQueries(session).count(User) == 1
    assert new_user.username == config.username
    assert new_user.check_password(config.password)


def test_get_user_returns_none(user):
    """Test that get_user returns None if the user cannot be found."""
    assert get_user(username=user.username, password='1234') is None
