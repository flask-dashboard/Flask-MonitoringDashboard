"""
    Use this file for migrating the Database from v1.X.X to v2.X.X
    Before running the script, make sure to change the OLD_DB_URL and NEW_DB_URL on lines 9 and 10.
    Refer to http://docs.sqlalchemy.org/en/latest/core/engines.html on how to configure this.
"""
import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

from flask_monitoringdashboard.database import Endpoint, Request, Outlier, Test, TestResult

# OLD_DB_URL = 'dialect+driver://username:password@host:port/old_db'
# NEW_DB_URL = 'dialect+driver://username:password@host:port/new_db'
OLD_DB_URL = 'sqlite:////home/bogdan/databases/flask-dashboard.db'
NEW_DB_URL = 'sqlite:////home/bogdan/databases/flask-dashboard-2.0.db'
# OLD_DB_URL = 'mysql+pymysql://root:admin@localhost/migration1'
# NEW_DB_URL = 'mysql+pymysql://root:admin@localhost/migration2'


TABLES = ["rules", "functionCalls", "outliers", "tests", "testRun"]
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
SEARCH_REQUEST_TIME = datetime.timedelta(seconds=10)

endpoint_dict = {}
outlier_dict = {}
tests_dict = {}


def create_new_db(db_url):
    from flask_monitoringdashboard.database import Base
    engine = create_engine(db_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    global DBSession
    DBSession = sessionmaker(bind=engine)


def get_connection(db_url):
    engine = create_engine(db_url)
    connection = engine.connect()
    return connection


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
    if isinstance(date_string, str):
        return datetime.datetime.strptime(date_string, DATE_FORMAT)
    return date_string


def move_rules(old_connection):
    rules = old_connection.execute("select * from {}".format(TABLES[0]))
    endpoints = []
    with session_scope() as db_session:
        for rule in rules:
            end = Endpoint(name=rule['endpoint'], monitor_level=rule['monitor'],
                           time_added=parse(rule['time_added']), version_added=rule['version_added'],
                           last_requested=parse(rule['last_accessed']))
            endpoints.append(end)
        db_session.bulk_save_objects(endpoints)


def populate_endpoint_dict(db_session):
    global endpoint_dict
    endpoints = db_session.query(Endpoint).all()
    for endpoint in endpoints:
        endpoint_dict[endpoint.name] = endpoint.id


def move_function_calls(old_connection):
    function_calls = old_connection.execute("select * from {}".format(TABLES[1]))
    requests = []
    with session_scope() as db_session:
        populate_endpoint_dict(db_session)
        for fc in function_calls:
            request = Request(endpoint_id=endpoint_dict[fc['endpoint']], duration=fc['execution_time'],
                              time_requested=parse(fc['time']), version_requested=fc['version'],
                              group_by=fc['group_by'], ip=fc['ip'])
            requests.append(request)
        db_session.bulk_save_objects(requests)


def get_request_id(requests, time, execution_time, start_index):
    for index, r in enumerate(requests):
        if index >= start_index:
            if abs(r.time_requested - parse(time)) < SEARCH_REQUEST_TIME and r.duration == execution_time:
                return r.id, index
    return None, start_index


def populate_outlier_dict(connection, db_session):
    global outlier_dict
    outliers = connection.execute("select * from {}".format(TABLES[2]))
    requests = db_session.query(Request).options(joinedload(Request.endpoint)).all()
    index = 0
    for outlier in outliers:
        req_id, index = get_request_id(requests, outlier['time'], outlier['execution_time'], start_index=index)
        outlier_dict[outlier['id']] = req_id


def move_outliers(old_connection):
    global outlier_dict
    old_outliers = old_connection.execute("select * from {}".format(TABLES[2]))
    outliers = []
    with session_scope() as db_session:
        populate_outlier_dict(old_connection, db_session)
        for o in old_outliers:
            outlier = Outlier(request_id=outlier_dict[o['id']], request_header=o['request_headers'],
                              request_environment=o['request_environment'], request_url=o['request_url'],
                              cpu_percent=o['cpu_percent'], memory=o['memory'], stacktrace=o['stacktrace'])
            outliers.append(outlier)
        db_session.bulk_save_objects(outliers)


def move_tests(old_connection):
    try:
        old_tests = old_connection.execute("select * from {}".format(TABLES[3]))
        tests = []
        with session_scope() as db_session:
            for t in old_tests:
                test = Test(name=t['name'], passing=t['succeeded'],
                            version_added='', last_tested=parse(t['lastRun']))
                tests.append(test)
            db_session.bulk_save_objects(tests)
    except Exception as err:
        print("tests table was not moved. Does the table exist?")
        print(err)


def populate_tests_dict(db_session):
    global tests_dict
    tests = db_session.query(Test).all()
    for test in tests:
        tests_dict[test.name] = test.id


def move_test_runs(old_connection):
    try:
        test_runs = old_connection.execute("select * from {}".format(TABLES[4]))
        test_results = []
        with session_scope() as db_session:
            populate_tests_dict(db_session)
            for tr in test_runs:
                test_result = TestResult(test_id=tests_dict[tr['name']], duration=tr['execution_time'],
                                         time_added=parse(tr['time']), app_version=tr['version'],
                                         travis_job_id=tr['suite'], run_nr=tr['run'])
                test_results.append(test_result)
            db_session.bulk_save_objects(test_results)
    except Exception as err:
        print("testRun table was not moved.")
        print(err)


def main():
    create_new_db(NEW_DB_URL)
    old_connection = get_connection(OLD_DB_URL)
    import timeit
    start = timeit.default_timer()
    move_rules(old_connection)
    t1 = timeit.default_timer()
    print("Moving rules took %f seconds" % (t1 - start))
    move_function_calls(old_connection)
    t2 = timeit.default_timer()
    print("Moving functionCalls took %f seconds" % (t2 - t1))
    move_outliers(old_connection)
    t3 = timeit.default_timer()
    print("Moving outliers took %f seconds" % (t3 - t2))
    move_tests(old_connection)
    t4 = timeit.default_timer()
    print("Moving tests took %f seconds" % (t4 - t3))
    move_test_runs(old_connection)
    t5 = timeit.default_timer()
    print("Moving testRuns took %f seconds" % (t5 - t4))

    print("Total time was %f seconds" % (t5 - start))


if __name__ == "__main__":
    main()
