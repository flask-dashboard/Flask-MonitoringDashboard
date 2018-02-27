"""
    Creates the database. 
    For information about how to access the database via a session-variable, see: session_scope() 
"""

from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_monitoringdashboard import config
from contextlib import contextmanager

Base = declarative_base()


class MonitorRule(Base):
    """ Table for storing which endpoints to monitor. """
    __tablename__ = 'rules'
    # endpoint must be unique and acts as a primary key
    endpoint = Column(String(250), primary_key=True)
    # boolean to determine whether the endpoint should be monitored?
    monitor = Column(Boolean, default=False)
    # the time and version on which the endpoint is added
    time_added = Column(DateTime)
    version_added = Column(String(100), nullable=False)
    # the timestamp of the last access time
    last_accessed = Column(DateTime)


class Tests(Base):
    """ Table for storing which tests to run. """
    __tablename__ = 'tests'
    # name must be unique and acts as a primary key
    name = Column(String(250), primary_key=True)
    # boolean to determine whether the test should be run
    run = Column(Boolean, default=True)
    # the timestamp of the last time the test was run
    lastRun = Column(DateTime)
    # whether the test succeeded
    succeeded = Column(Boolean)


class TestRun(Base):
    """ Table for storing test results. """
    __tablename__ = 'testRun'
    # name of executed test
    name = Column(String(250), primary_key=True)
    # execution_time in ms
    execution_time = Column(Float, primary_key=True)
    # time of adding the result to the database
    time = Column(DateTime, primary_key=True)
    # version of the website at the moment of adding the result to the database
    version = Column(String(100), nullable=False)
    # number of the test suite execution
    suite = Column(Integer)
    # number describing the i-th run of the test within the suite
    run = Column(Integer)


class FunctionCall(Base):
    """ Table for storing measurements of function calls. """
    __tablename__ = 'functionCalls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(250), nullable=False)
    # execution_time in ms
    execution_time = Column(Float, nullable=False)
    # time of adding the result to the database
    time = Column(DateTime)
    # version of the website at the moment of adding the result to the database
    version = Column(String(100), nullable=False)
    # which user is calling the function
    group_by = Column(String(100), nullable=False)
    # ip address of remote user
    ip = Column(String(25), nullable=False)


class Outlier(Base):
    """ Table for storing information about outliers. """
    __tablename__ = 'outliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(250), nullable=False)

    # request-values, GET, POST, PUT
    request_values = Column(String(10000))
    # request headers
    request_headers = Column(String(10000))
    # request environment
    request_environment = Column(String(10000))
    # request url
    request_url = Column(String(1000))

    # cpu_percent in use
    cpu_percent = Column(String(100))
    # memory
    memory = Column(String(10000))

    # stacktrace
    stacktrace = Column(String(100000))

    # execution_time in ms
    execution_time = Column(Float, nullable=False)
    # time of adding the result to the database
    time = Column(DateTime)


class TestsGrouped(Base):
    """ Table for storing grouped tests on endpoints. """
    __tablename__ = 'testsGrouped'
    # Name of the endpoint
    endpoint = Column(String(250), primary_key=True)
    # Name of the unit test
    test_name = Column(String(250), primary_key=True)


# define the database
engine = create_engine(config.database_name)

# creates all tables in the database
Base.metadata.create_all(engine)
Base.metadata.bind = engine
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
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_tables():
    """ Returns a list of Base-objects. This are all tables in the database"""
    return [MonitorRule, Tests, TestRun, FunctionCall, Outlier, TestsGrouped]
