"""
    Use this file for migrating the Database from v1.X.X to v2.X.X
    Before running the script, make sure to change the OLD_DB_URL and NEW_DB_URL on lines 9 and 10.
    Refer to http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure this.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

from sqlalchemy.ext.declarative import declarative_base

# DB_URL = 'dialect+driver://username:password@host:port/db'
DB_URL = 'sqlite:////Users/johan/Projects/Flask-MonitoringDashboard/flask_monitoringdashboard/data.db'
# DB_URL = 'mysql+pymysql://root:admin@localhost/migration1'


engine = create_engine(DB_URL)

Base = declarative_base()
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

connection = engine.connect()



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


def main():
    print("Starting migration")

    with session_scope() as db_session:
        try:
            results = connection.execute("ALTER TABLE request ADD COLUMN status_code INT NULLABLE")
        except:
            print("Column already exists")

    print("Finished.")


if __name__ == "__main__":
    main()
