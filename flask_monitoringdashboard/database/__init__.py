"""
    Creates the database. 
    For information about how to access the database via a session-variable, see: session_scope() 
"""
import datetime
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float, Boolean, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.group_by import get_group_by

Base = declarative_base()


class MonitorRule(Base):
    """ Table for storing which endpoints to monitor. """
    __tablename__ = 'rules'
    # endpoint must be unique and acts as a primary key
    endpoint = Column(String(250), primary_key=True)
    # boolean to determine whether the endpoint should be monitored?
    monitor = Column(Boolean, default=config.default_monitor)
    # the time and version on which the endpoint is added
    time_added = Column(DateTime)
    version_added = Column(String(100), default=config.version)
    # the timestamp of the last access time
    last_accessed = Column(DateTime)


class FunctionCall(Base):
    """ Table for storing measurements of function calls. """
    __tablename__ = 'functionCalls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(250), nullable=False)
    # execution_time in ms
    execution_time = Column(Float, nullable=False)
    # time of adding the result to the database
    time = Column(DateTime, default=datetime.datetime.utcnow)
    # version of the website at the moment of adding the result to the database
    version = Column(String(100), nullable=False)
    # which user is calling the function
    group_by = Column(String(100), default=get_group_by)
    # ip address of remote user
    ip = Column(String(25), nullable=False)


class Outlier(Base):
    """ Table for storing information about outliers. """
    __tablename__ = 'outliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(250), nullable=False)

    # request-values, GET, POST, PUT
    request_values = Column(TEXT)
    # request headers
    request_headers = Column(TEXT)
    # request environment
    request_environment = Column(TEXT)
    # request url
    request_url = Column(String(1000))

    # cpu_percent in use
    cpu_percent = Column(String(100))
    # memory
    memory = Column(TEXT)

    # stacktrace
    stacktrace = Column(TEXT)

    # execution_time in ms
    execution_time = Column(Float, nullable=False)
    # time of adding the result to the database
    time = Column(DateTime)


class TestRun(Base):
    """ Stores unit test performance results obtained from Travis. """
    __tablename__ = 'testRun'
    # name of executed test
    name = Column(String(250), primary_key=True)
    # execution_time in ms
    execution_time = Column(Float, primary_key=True)
    # time of adding the result to the database
    time = Column(DateTime, primary_key=True)
    # version of the user app that was tested
    version = Column(String(100), nullable=False)
    # number of the test suite execution
    suite = Column(Integer)
    # number describing the i-th run of the test within the suite
    run = Column(Integer)


class TestsGrouped(Base):
    """ Stores which endpoints are tested by which unit tests. """
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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_tables():
    return [MonitorRule, FunctionCall, Outlier, TestRun, TestsGrouped]
