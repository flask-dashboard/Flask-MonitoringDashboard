"""
    Use this file for migrating the Database from v1.X.X to v2.X.X
    Before running the script, make sure to change the OLD_DB_URL and NEW_DB_URL on lines 9 and 10.
    Refer to http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure this.
"""
import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask_monitoringdashboard.database import Endpoint

# OLD_DB_URL = 'dialect+driver://username:password@host:port/old_db'
# NEW_DB_URL = 'dialect+driver://username:password@host:port/new_db'
OLD_DB_URL = 'sqlite://///home/bogdan/school_tmp/RI/stacktrace_view/copy.db'
NEW_DB_URL = 'sqlite://///home/bogdan/school_tmp/RI/stacktrace_view/new.db'
TABLES = ["rules", "functionCalls", "outliers", "testRun", "testsGrouped"]
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def create_new_db(db_url):
    from flask_monitoringdashboard.database import Base
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    global DBSession
    DBSession = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """
    When accessing the database, use the following syntax:
        with session_scope() as db_session:
            db_session.query(...)

    :return: the session for accessing the database
    """
    session = DBSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session(db_url):
    """This creates the new database and returns the session scope."""
    from flask_monitoringdashboard import config
    config.database_name = db_url

    import flask_monitoringdashboard.database
    return flask_monitoringdashboard.database.session_scope()


def parse(date_string):
    if not date_string:
        return None
    return datetime.datetime.strptime(date_string, DATE_FORMAT)


def move_rules(old_connection):
    rules = old_connection.execute("select * from {}".format(TABLES[0]))
    with session_scope() as db_session:
        for rule in rules:
            end = Endpoint(name=rule['endpoint'], monitor_level=rule['monitor'],
                           time_added=parse(rule['time_added']), version_added=rule['version_added'],
                           last_requested=parse(rule['last_accessed']))
            db_session.add(end)


def move_function_calls(old_connection):
    print()


def get_connection(db_url):
    engine = create_engine(db_url)
    connection = engine.connect()
    return connection


def main():
    create_new_db(NEW_DB_URL)
    old_connection = get_connection(OLD_DB_URL)
    move_rules(old_connection)


if __name__ == "__main__":
    main()
