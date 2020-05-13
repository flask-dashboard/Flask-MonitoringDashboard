"""
    Use this file for migrating the Database such that status codes can be tracked.
    Before running the script, make sure to specify DB_URL on line 15
    Refer to http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure this.
"""
from contextlib import contextmanager


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

# DB_URL = 'dialect+driver://username:password@host:port/db'
DB_URL = 'mysql+pymysql://user:password@localhost:3306/database'

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
        with session_scope() as session:
            session.query(...)

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

    with session_scope():
        try:
            connection.execute("ALTER TABLE Request ADD COLUMN status_code INT")
        except Exception as e:
            print("Column already exists: {}".format(e))

    print("Finished.")


if __name__ == "__main__":
    main()
