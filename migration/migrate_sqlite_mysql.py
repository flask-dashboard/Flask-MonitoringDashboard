"""
    Use this file for migrating your data from SQLite to MySQL. It only works for version >=2.0.0 of the Flask
    Monitoring Dashboard. For migrating your data from version 1.x.x to 2.y.y, use the script "migrate_v1_to_v2.py".

    Before running the script, make sure to change the SQLITE_URL and MYSQL_URL variables. Refer to
    http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure them. Also, make sure MySQL Server
    is running on your machine.
"""
import timeit

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask_monitoringdashboard.database import Base, Endpoint, Request, Outlier, CodeLine, StackLine, Test, \
    TestResult, TestEndpoint

SQLITE_URL = 'sqlite:////Users/bogdan/Flask-MonitoringDashboard/fmd_copy.db'
MYSQL_URL = 'mysql+pymysql://bogdan:bogdan@localhost:3306/db2'
ENTITIES = [Endpoint, Request, Outlier, CodeLine, StackLine, Test, TestResult, TestEndpoint]


def create_db_session(db_url, clean=False):
    engine = create_engine(db_url)
    if clean:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    return sessionmaker(bind=engine)


@contextmanager
def session_scope(db_session):
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_old_instances(db_session_old, entity_class):
    with session_scope(db_session_old) as db_session:
        old_instances = db_session.query(entity_class).all()
        db_session.expunge_all()
    return old_instances


def migrate_entity(db_session_old, db_session_new, entity_class):
    old_instances = get_old_instances(db_session_old, entity_class)
    new_instances = []
    with session_scope(db_session_new) as db_session:
        for old_instance in old_instances:
            del old_instance.__dict__['_sa_instance_state']
            new_instances.append(entity_class(**old_instance.__dict__))
        db_session.bulk_save_objects(new_instances)


def main():
    db_session_old = create_db_session(SQLITE_URL)
    db_session_new = create_db_session(MYSQL_URL, clean=True)
    t0 = timeit.default_timer()
    t_previous = t0
    for entity_class in ENTITIES:
        migrate_entity(db_session_old, db_session_new, entity_class)
        t_now = timeit.default_timer()
        print("Moving %s took %f seconds" % (entity_class.__name__, t_now - t_previous))
        t_previous = t_now
    print("Total time was %f seconds" % (t_previous - t0))


if __name__ == "__main__":
    main()
