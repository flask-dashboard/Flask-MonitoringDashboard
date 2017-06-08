"""
Contains all functions that access the settings-table from the database.
"""
from sqlalchemy.orm.exc import NoResultFound
from dashboard.database import session_scope, Setting


def get_setting(name, default):
    """
    Returns the value of the variable 'name' that is returned from the database.
    If such a variable does not exists, a row with value 'default' is added to the database.
    :param name: the name of the variable
    :param default: the default value when a new row is added
    :return: the value retrieved from the database
    """
    try:
        with session_scope() as db_session:
            result = db_session.query(Setting).filter(Setting.variable == name).one()
            db_session.expunge(result)
        return result.value
    except NoResultFound:
        with session_scope() as db_session:
            db_session.add(Setting(variable=name, value=default))
        return default


def set_setting(name, value):
    """ Updates a row in the database with a new value. """
    with session_scope() as db_session:
        db_session.query(Setting).filter(Setting.variable == name). \
            update({Setting.value: value})
