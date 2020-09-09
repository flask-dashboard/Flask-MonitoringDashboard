"""
    Use this file for migrating your data from SQLite to MySQL. It only works for version >=2.0.0
    of the Flask Monitoring Dashboard. For migrating your data from version 1.x.x to 2.y.y, use
    the script "migrate_v1_to_v2.py".

    Before running the script, make sure to change the SQLITE_URL and MYSQL_URL variables. Refer to
    http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure them. Also, make sure
    MySQL Server is running on your machine.
"""
import timeit

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask_monitoringdashboard.database import Base, Endpoint, Request, Outlier, CodeLine, StackLine

SQLITE_URL = 'sqlite:////Users/user/Flask-MonitoringDashboard/fmd.db'
MYSQL_URL = 'mysql+pymysql://user:password@localhost:3306/database'
ENTITIES = [Endpoint, Request, Outlier, CodeLine, StackLine]
CHUNK_SIZE = 10000


def create_db_session(db_url, clean=False):
    engine = create_engine(db_url)
    if clean:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    return sessionmaker(bind=engine)


@contextmanager
def session_scope(session):
    session = session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_row_count(db_session_old, entity_class):
    with session_scope(db_session_old) as session:
        count = session.query(entity_class).count()
        session.expunge_all()
    return count


def get_old_instances(db_session_old, entity_class, start, end):
    with session_scope(db_session_old) as session:
        old_instances = session.query(entity_class).slice(start, end).all()
        session.expunge_all()
    return old_instances


def migrate_batch(old_instances, db_session_new, entity_class):
    new_instances = []
    with session_scope(db_session_new) as session:
        for (index, old_instance) in enumerate(old_instances):
            # _sa_instance_state is a non-db value used internally by SQLAlchemy
            del old_instance.__dict__['_sa_instance_state']
            new_instances.append(entity_class(**old_instance.__dict__))
        session.bulk_save_objects(new_instances)


def migrate_all(db_session_old, db_session_new, entity_class, count):
    chunks = count // CHUNK_SIZE
    for i in range(chunks + 1):
        print("Moving batch %d of %d for entity %s..." % (i + 1, chunks + 1, entity_class.__name__))
        old_instances = get_old_instances(
            db_session_old, entity_class, i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE
        )
        migrate_batch(old_instances, db_session_new, entity_class)


def main():
    db_session_old = create_db_session(SQLITE_URL)
    db_session_new = create_db_session(MYSQL_URL, clean=True)
    t0 = timeit.default_timer()
    t_previous = t0
    for entity_class in ENTITIES:
        count = get_row_count(db_session_old, entity_class)
        migrate_all(db_session_old, db_session_new, entity_class, count)
        t_now = timeit.default_timer()
        print("Moving %s took %f seconds" % (entity_class.__name__, t_now - t_previous))
        t_previous = t_now
    print("Total time was %f seconds" % (t_previous - t0))


if __name__ == "__main__":
    main()
