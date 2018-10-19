"""
    Use this file for migrating your data from SQLite to MySQL. It only works for version >=2.0.0 of the Flask
    Monitoring Dashboard. For migrating your data from version 1.x.x to 2.y.y, use the script "migrate_v1_to_v2.py".

    Before running the script, make sure to change the SQLITE_URL and MYSQL_URL variables.
    Refer to http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure this.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import Endpoint, Request

SQLITE_URL = 'sqlite:////Users/bogdan/Flask-MonitoringDashboard/fmd_copy.db'
MYSQL_URL = 'mysql+pymysql://bogdan:bogdan@localhost:3306/db2'
TABLES = ['{}Endpoint'.format(config.table_prefix), '{}Request'.format(config.table_prefix),
          '{}Outlier'.format(config.table_prefix), '{}CodeLine'.format(config.table_prefix),
          '{}StackLine'.format(config.table_prefix), '{}Test'.format(config.table_prefix),
          '{}TestResult'.format(config.table_prefix), '{}TestEndpoint'.format(config.table_prefix)]


def old_db_session(db_url):
    from flask_monitoringdashboard.database import Base
    engine = create_engine(db_url)
    Base.metadata.bind = engine
    global DBSession1
    DBSession1 = sessionmaker(bind=engine)


def create_new_db(db_url):
    from flask_monitoringdashboard.database import Base
    engine = create_engine(db_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    global DBSession2
    DBSession2 = sessionmaker(bind=engine)


def get_connection(db_url):
    engine = create_engine(db_url)
    connection = engine.connect()
    return connection


@contextmanager
def session_scope1():
    """
    When accessing the database, use the following syntax:
        with session_scope() as db_session:
            db_session.query(...)

    :return: the session for accessing the database
    """
    session = DBSession1()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope2():
    """
    When accessing the database, use the following syntax:
        with session_scope() as db_session:
            db_session.query(...)

    :return: the session for accessing the database
    """
    session = DBSession2()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def move_endpoints():
    with session_scope1() as db_session1:
        endpoints_old = db_session1.query(Endpoint).all()
        db_session1.expunge_all()

    endpoints_new = []
    with session_scope2() as db_session2:
        for end in endpoints_old:
            endpoints_new.append(Endpoint(id=end.id, name=end.name, monitor_level=end.monitor_level,
                                          time_added=end.time_added, version_added=end.version_added,
                                          last_requested=end.last_requested))
        db_session2.bulk_save_objects(endpoints_new)


def move_requests():
    with session_scope1() as db_session1:
        requests_old = db_session1.query(Request).all()
        db_session1.expunge_all()

    requests_new = []
    with session_scope2() as db_session2:
        for r in requests_old:
            requests_new.append(Request(id=r.id, endpoint_id=r.endpoint_id, duration=r.duration,
                                        time_requested=r.time_requested, version_requested=r.version_requested,
                                        group_by=r.group_by, ip=r.ip))
        db_session2.bulk_save_objects(requests_new)


def main():
    old_db_session(SQLITE_URL)
    create_new_db(MYSQL_URL)
    import timeit
    start = timeit.default_timer()
    move_endpoints()
    t1 = timeit.default_timer()
    print("Moving endpoints took %f seconds" % (t1 - start))
    move_requests()
    t2 = timeit.default_timer()
    print("Moving endpoints took %f seconds" % (t2 - t1))

    print("Total time was %f seconds" % (t2 - start))


if __name__ == "__main__":
    main()
