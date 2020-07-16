from flask_monitoringdashboard.database import User
from flask_monitoringdashboard.database.auth import get_user


def test_get_user_adds_default(session, config):
    session.query(User).delete()  # delete all existing users
    session.commit()
    new_user = get_user(config.username, config.password)

    assert session.query(User).count() == 1

    assert new_user.username == config.username
    assert new_user.check_password(config.password)


def test_get_user_returns_none(user):
    """Test that get_user returns None if the user cannot be found."""
    assert get_user(username=user.username, password='1234') is None
