"""
    Creates the database. 
    For information about how to access the database via a session-variable, see: session_scope() 
"""
import datetime
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float, Boolean, TEXT, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.group_by import get_group_by

Base = declarative_base()


class Endpoint(Base):
    """ Table for storing information about the endpoints. """
    __tablename__ = '{}Endpoint'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    # name of the endpoint
    name = Column(String(250), unique=True, nullable=False)
    # 0 - disabled, 1 - performance, 2 - profiler, 3 - profiler + outliers
    monitor_level = Column(Integer, default=config.monitor_level)
    # the time when the endpoint was added
    time_added = Column(DateTime, default=datetime.datetime.utcnow)
    # the version when the endpoint was added
    version_added = Column(String(100), default=config.version)
    # the time the endpoint was last used
    last_requested = Column(DateTime)


class Request(Base):
    """ Table for storing measurements of requests. """
    __tablename__ = '{}Request'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    endpoint_id = Column(Integer, ForeignKey(Endpoint.id))
    # the processing time of the request
    duration = Column(Float, nullable=False)
    # the time when the request was handled
    time_requested = Column(DateTime, default=datetime.datetime.utcnow)
    # the version when the request was handled
    version_requested = Column(String(100), default=config.version)
    # a criteria by which the requests can be grouped
    group_by = Column(String(100), default=get_group_by)
    # the ip address of the requester
    ip = Column(String(100), nullable=False)

    endpoint = relationship(Endpoint)
    stack_lines = relationship('StackLine', back_populates='request')
    outlier = relationship('Outlier', uselist=False, back_populates='request')


class Outlier(Base):
    """ Table for storing information about outliers. """
    __tablename__ = '{}Outlier'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey(Request.id))
    # http headers of the request
    request_header = Column(TEXT)
    # http environment of the request
    request_environment = Column(TEXT)
    # url of the request
    request_url = Column(String(2100))
    # cpu utilization of the server when handling the request
    cpu_percent = Column(String(150))
    # memory utilization of the server when handling the request
    memory = Column(TEXT)
    # the stacktrace of the request
    stacktrace = Column(TEXT)

    request = relationship(Request, back_populates='outlier')


class CodeLine(Base):
    __tablename__ = '{}CodeLine'.format(config.table_prefix)
    """ Table for storing the text of a StackLine. """
    id = Column(Integer, primary_key=True)
    # quadruple (filename, line_number, function_name, code) that uniquely identifies a statement in the code
    filename = Column(String(250), nullable=False)
    line_number = Column(Integer, nullable=False)
    function_name = Column(String(250), nullable=False)
    code = Column(String(250), nullable=False)


class StackLine(Base):
    """ Table for storing lines of execution paths of calls. """
    __tablename__ = '{}StackLine'.format(config.table_prefix)
    request_id = Column(Integer, ForeignKey(Request.id), primary_key=True)
    code_id = Column(Integer, ForeignKey(CodeLine.id))
    # position in the flattened stack tree
    position = Column(Integer, primary_key=True)
    # level in the tree
    indent = Column(Integer, nullable=False)
    # time spent on that line
    duration = Column(Float, nullable=False)

    request = relationship(Request, back_populates='stack_lines')
    code = relationship(CodeLine)


class Test(Base):
    """ Stores all of the tests that exist in the project. """
    __tablename__ = '{}Test'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    # name of the test
    name = Column(String(250), unique=True)
    # true - the test passed, false - otherwise
    passing = Column(Boolean, nullable=False)
    # time of the most recent run of the test
    last_tested = Column(DateTime, default=datetime.datetime.utcnow)
    # version when the test was added
    version_added = Column(String(100), nullable=False)
    # time when the test was added
    time_added = Column(DateTime, default=datetime.datetime.utcnow)


class TestResult(Base):
    """ Stores unit test performance results obtained from Travis. """
    __tablename__ = '{}TestResult'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey(Test.id))
    # time it took to run the test
    duration = Column(Float, nullable=False)
    # time when the test was run
    time_added = Column(DateTime, default=datetime.datetime.utcnow)
    # version when the test was run
    app_version = Column(String(100), nullable=False)
    # id of the travis job running the test
    travis_job_id = Column(String(10), nullable=False)
    # number of the travis run
    run_nr = Column(Integer, nullable=False)

    test = relationship(Test)


class TestEndpoint(Base):
    """ Stores the endpoint hits that came from unit tests. """
    __tablename__ = '{}TestEndpoint'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    endpoint_id = Column(Integer, ForeignKey(Endpoint.id))
    test_id = Column(Integer, ForeignKey(Test.id))
    # duration of the tests for an endpoint
    duration = Column(Float, nullable=False)
    # version when the endpoint was tested
    app_version = Column(String(100), nullable=False)
    # id of the travis job running the test
    travis_job_id = Column(String(10), nullable=False)
    # time when the endpoint was tested
    time_added = Column(DateTime, default=datetime.datetime.utcnow)

    endpoint = relationship(Endpoint)
    test = relationship(Test)


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
    session_obj = scoped_session(DBSession)
    session = session_obj()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_tables():
    return [Endpoint, Request, Outlier, StackLine, CodeLine, Test, TestResult, TestEndpoint]
