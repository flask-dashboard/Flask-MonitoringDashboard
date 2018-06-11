"""
    Creates the database. 
    For information about how to access the database via a session-variable, see: session_scope() 
"""
import datetime
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float, Boolean, TEXT, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.group_by import get_group_by

Base = declarative_base()


class Endpoint(Base):
    """ Table for storing which endpoints to monitor. """
    __tablename__ = '{}Endpoint'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    monitor_level = Column(Integer, default=config.monitor_level)
    # the time and version on which the endpoint is added
    time_added = Column(DateTime, default=datetime.datetime.utcnow)
    version_added = Column(String(100), default=config.version)

    last_requested = Column(DateTime)


class Request(Base):
    """ Table for storing measurements of function calls. """
    __tablename__ = '{}Request'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    endpoint_id = Column(Integer, ForeignKey(Endpoint.id))
    endpoint = relationship(Endpoint)

    stack_lines = relationship('StackLine', back_populates='request')

    duration = Column(Float, nullable=False)
    time_requested = Column(DateTime, default=datetime.datetime.utcnow)
    version_requested = Column(String(100), default=config.version)

    group_by = Column(String(100), default=get_group_by)
    ip = Column(String(100), nullable=False)

    outlier = relationship('Outlier', uselist=False, back_populates='request')


class Outlier(Base):
    """ Table for storing information about outliers. """
    __tablename__ = '{}Outlier'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey(Request.id))
    request = relationship(Request, back_populates='outlier')

    request_header = Column(TEXT)
    request_environment = Column(TEXT)
    request_url = Column(String(2100))

    # cpu_percent in use
    cpu_percent = Column(String(150))
    memory = Column(TEXT)
    stacktrace = Column(TEXT)


class CodeLine(Base):
    __tablename__ = '{}CodeLine'.format(config.table_prefix)
    """ Table for storing the text of a StackLine. """
    id = Column(Integer, primary_key=True)
    filename = Column(String(250), nullable=False)
    line_number = Column(Integer, nullable=False)
    function_name = Column(String(250), nullable=False)
    code = Column(String(250), nullable=False)


class StackLine(Base):
    """ Table for storing lines of execution paths of calls. """
    __tablename__ = '{}StackLine'.format(config.table_prefix)
    request_id = Column(Integer, ForeignKey(Request.id), primary_key=True)
    request = relationship(Request, back_populates='stack_lines')
    position = Column(Integer, primary_key=True)

    # level in the tree
    indent = Column(Integer, nullable=False)
    # text of the line
    code_id = Column(Integer, ForeignKey(CodeLine.id))
    code = relationship(CodeLine)
    # time elapsed on that line
    duration = Column(Float, nullable=False)


class Test(Base):
    """ Stores all of the tests that exist in the project. """
    __tablename__ = '{}Test'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True)
    passing = Column(Boolean, nullable=False)
    last_tested = Column(DateTime, default=datetime.datetime.utcnow)
    version_added = Column(String(100), nullable=False)
    time_added = Column(DateTime, default=datetime.datetime.utcnow)


class TestResult(Base):
    """ Stores unit test performance results obtained from Travis. """
    __tablename__ = '{}TestResult'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey(Test.id))
    test = relationship(Test)
    duration = Column(Float, nullable=False)
    time_added = Column(DateTime, default=datetime.datetime.utcnow)
    app_version = Column(String(100), nullable=False)
    travis_job_id = Column(String(10), nullable=False)
    run_nr = Column(Integer, nullable=False)


class TestEndpoint(Base):
    """ Stores the endpoint hits that came from unit tests. """
    __tablename__ = '{}TestEndpoint'.format(config.table_prefix)
    id = Column(Integer, primary_key=True)
    endpoint_id = Column(Integer, ForeignKey(Endpoint.id))
    endpoint = relationship(Endpoint)
    test_id = Column(Integer, ForeignKey(Test.id))
    test = relationship(Test)
    duration = Column(Float, nullable=False)
    app_version = Column(String(100), nullable=False)
    travis_job_id = Column(String(10), nullable=False)
    time_added = Column(DateTime, default=datetime.datetime.utcnow)


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
    return [Endpoint, Request, Outlier, StackLine, CodeLine, Test, TestResult, TestEndpoint]
