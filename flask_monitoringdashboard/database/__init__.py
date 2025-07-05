"""Creates the database.
For information about how to access the database via a session-variable, see: session_scope()
"""

import datetime
import random
import time
import uuid
from contextlib import contextmanager

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    create_engine,
    Float,
    TEXT,
    ForeignKey,
    exc,
)

try:
    # the declarative API is a part of the ORM layer since SQLAlchemy 1.4
    from sqlalchemy.orm import declarative_base
except ImportError:
    # however it used to be an extension before SQLAlchemy 1.4
    from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash

from flask_monitoringdashboard import config

Base = declarative_base()


class User(Base):
    """Table for storing user management."""

    __tablename__ = "{}User".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    username = Column(String(250), unique=True, nullable=False)
    """Username for logging into the FMD."""

    password_hash = Column(String(162), nullable=False)
    """Hashed password."""

    is_admin = Column(Boolean, default=False)
    """False for guest permissions (only view access). True for admin permissions."""

    def set_password(self, password):
        # Using the pbkdf2 because it scrypt won't work on a Mac M1 with Sequoia
        self.password_hash = generate_password_hash(password, "pbkdf2")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TelemetryUser(Base):
    """Table for storing a unique identifier of an FMD user"""

    __tablename__ = "{}TelemetryUser".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(String(40), primary_key=True, default=str(uuid.uuid4()))
    """Unique anonymous identifier to group the data received through telemetry"""

    times_initialized = Column(Integer, default=1)
    """For checking the amount of times the app was initialized"""

    last_initialized = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    """Check when was the last time user accessed FMD"""

    monitoring_consent = Column(Integer, default=1)
    """If user agrees to share data 1 - not responded 2 - declined 3 - accepted"""


class Endpoint(Base):
    """Table for storing information about the endpoints."""

    __tablename__ = "{}Endpoint".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    name = Column(String(250), unique=True, nullable=False)
    """Name of the endpoint."""

    monitor_level = Column(Integer, default=config.monitor_level)
    """0 - disabled, 1 - performance, 2 - outliers, 3 - profiler + outliers"""

    time_added = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    """Time when the endpoint was added."""

    version_added = Column(String(100), default=config.version)
    """Version when the endpoint was added into the DB."""

    last_requested = Column(DateTime)
    """Time when the endpoint was last requested."""


class Request(Base):
    """Table for storing measurements of requests."""

    __tablename__ = "{}Request".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    endpoint_id = Column(Integer, ForeignKey(Endpoint.id))
    endpoint = relationship(Endpoint, backref="requests")
    """The endpoint that handles the request."""

    duration = Column(Float, nullable=False)
    """Processing time of the request in milliseconds."""

    time_requested = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    """Moment when the request was handled."""

    version_requested = Column(String(100), default=config.version)
    """Version when the request was handled."""

    group_by = Column(String(100), default=None)
    """Criteria which can be used for grouping multiple requests."""

    ip = Column(String(100), nullable=False)
    """IP address of the requester."""

    status_code = Column(Integer, nullable=True)
    """HTTP status code of the request."""

    outlier = relationship("Outlier", uselist=False, back_populates="request")


class Outlier(Base):
    """Table for storing information about outliers."""

    __tablename__ = "{}Outlier".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    request_id = Column(Integer, ForeignKey(Request.id))
    request = relationship(Request, back_populates="outlier")
    """Request of the outlier."""

    request_header = Column(TEXT)
    """HTTP headers of the request."""

    request_environment = Column(TEXT)
    """HTTP environment of the request."""

    request_url = Column(String(2100))
    """Request URL."""

    cpu_percent = Column(String(150))
    """CPU percent of the request at the moment of handling the request."""

    memory = Column(TEXT)
    """Memory utilization of the server when handling the request."""

    stacktrace = Column(TEXT)
    """Stacktrace of the request."""


class CodeLine(Base):
    """Table for storing the text of a StackLine.
    This is a quadruple (filename, line_number, function_name, code) that uniquely
    identifies a line in the code."""

    __tablename__ = "{}CodeLine".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    filename = Column(String(250), nullable=False)
    """Filename that contains the line."""

    line_number = Column(Integer, nullable=False)
    """The line_number itself."""

    function_name = Column(String(250), nullable=False)
    """The function that contains this line."""

    code = Column(String(250), nullable=False)
    """The actual text (white spaces are stripped)."""


class StackLine(Base):
    """Table for storing lines of execution paths of calls."""

    __tablename__ = "{}StackLine".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    request_id = Column(Integer, ForeignKey(Request.id), primary_key=True)
    request = relationship(Request, backref="stack_lines")
    """Request that belongs to this stack_line."""

    code_id = Column(Integer, ForeignKey(CodeLine.id))
    code = relationship(CodeLine)
    """Corresponding codeline."""

    position = Column(Integer, primary_key=True)
    """Position in the flattened stack tree."""

    indent = Column(Integer, nullable=False)
    """Level in the tree."""

    duration = Column(Float, nullable=False)
    """Time spend in this specific code_line."""


class CustomGraph(Base):
    """Table for storing custom graphs names."""

    __tablename__ = "{}CustomGraph".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    graph_id = Column(Integer, primary_key=True)

    title = Column(String(250), nullable=False, unique=True)
    """Title of this graph."""

    time_added = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    """When the graph was first added to the dashboard."""

    version_added = Column(String(100), default=config.version)
    """Version when the graph was added."""


class CustomGraphData(Base):
    """Table for storing data collected by custom graphs."""

    __tablename__ = "{}CustomGraphData".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    graph_id = Column(Integer, ForeignKey(CustomGraph.graph_id))
    graph = relationship(CustomGraph, backref="data")
    """Graph for which the data is collected."""

    time = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    """Moment when the data is collected."""

    value = Column(Float)
    """Actual value that is measured."""


class StackTraceSnapshot(Base):
    """Table for storing a hash of a stack trace and its related functions, to avoid 'duplicate' ExceptionStackLines."""

    __tablename__ = "{}StackTraceSnapshot".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=False, unique=True)

    exception_stack_lines = relationship(
        "ExceptionStackLine", back_populates="stack_trace_snapshot"
    )


class ExceptionType(Base):
    """Table for storing Exception types"""

    __tablename__ = "{}ExceptionType".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)
    type = Column(String(256), nullable=False)


class ExceptionMessage(Base):
    """Table for storing Exception messages"""

    __tablename__ = "{}ExceptionMessage".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)
    message = Column(TEXT, nullable=False)


class ExceptionOccurrence(Base):
    """Table for storing exception id together with request id."""

    __tablename__ = "{}ExceptionOccurrence".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    request_id = Column(Integer, ForeignKey(Request.id))
    request = relationship(Request)

    exception_type_id = Column(Integer, ForeignKey(ExceptionType.id), nullable=False)
    exception_type = relationship(ExceptionType)

    exception_msg_id = Column(Integer, ForeignKey(ExceptionMessage.id), nullable=False)
    exception_msg = relationship(ExceptionMessage)

    stack_trace_snapshot_id = Column(
        Integer, ForeignKey(StackTraceSnapshot.id), nullable=False
    )
    stack_trace_snapshot = relationship(StackTraceSnapshot)

    is_user_captured = Column(Boolean, nullable=False)


class FunctionDefinition(Base):
    """Table for storing entire functions for better logging"""

    __tablename__ = f"{config.table_prefix}FunctionDefinition"
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    name = Column(String(256), nullable=True)
    """The name of the function"""

    code = Column(TEXT, nullable=True)
    """The entire function code"""

    code_hash = Column(String(64), nullable=True)
    """The hash of the function code"""


class FilePath(Base):
    """Table for storing file paths"""

    __tablename__ = "{}FilePath".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)
    path = Column(String(250), nullable=False, unique=True)


class FunctionLocation(Base):
    """Table for storing functions with their locations in the source code"""

    __tablename__ = "{}FunctionLocation".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    file_path_id = Column(Integer, ForeignKey(FilePath.id))
    file_path = relationship(FilePath)
    """The file path of the file where the function is located"""

    function_definition_id = Column(Integer, ForeignKey(FunctionDefinition.id))
    function_definition = relationship(FunctionDefinition)
    """The related function definition"""

    function_start_line_number = Column(Integer, nullable=False)
    """The starting line number of the function in the source file"""


class ExceptionFrame(Base):
    """Table for storing information of a frame in an exceptions traceback"""

    __tablename__ = "{}ExceptionFrame".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    id = Column(Integer, primary_key=True)

    function_location_id = Column(Integer, ForeignKey(FunctionLocation.id))
    function_location = relationship(FunctionLocation)
    """The location of the function that the frame points to"""

    line_number = Column(Integer, nullable=False)
    """The line number in the file the frame points to"""


class ExceptionStackLine(Base):
    """Table for storing exception id together with request id."""

    __tablename__ = "{}ExceptionStackLine".format(config.table_prefix)
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}

    stack_trace_snapshot_id = Column(
        Integer, ForeignKey(StackTraceSnapshot.id), primary_key=True
    )
    stack_trace_snapshot = relationship(
        StackTraceSnapshot, back_populates="exception_stack_lines"
    )
    """Stack trace that belongs to this exc_stack_line."""

    exception_frame_id = Column(
        Integer, ForeignKey(ExceptionFrame.id), primary_key=True
    )
    exception_frame = relationship(ExceptionFrame)
    """The frame that belongs to this exc_stack_line."""

    position = Column(Integer, primary_key=True)
    """Position in the flattened stack tree."""


# define the database
engine = create_engine(config.database_name)
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """When accessing the database, use the following syntax:
    >>> with session_scope() as session:
    >>>     session.query(...)
    :return: the session for accessing the database.
    """
    session_obj = scoped_session(DBSession)
    session = session_obj()
    try:
        yield session
        session.commit()
    except exc.OperationalError as e:
        print("Will retry commit, due to the following error: {}".format(e))
        session.rollback()
        time.sleep(0.5 + random.random())
        session.commit()
    except Exception as e:
        session.rollback()
        print("No commit has been made, due to the following error: {}".format(e))
    finally:
        session.close()


def row2dict(row):
    """Converts a database-object to a python dict.
    This function can be used to serialize an object into JSON, as this cannot be
    directly done (but a dict can).
    :param row: any object
    :return: dict
    """
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def get_tables():
    return [
        Endpoint,
        Request,
        Outlier,
        StackLine,
        CodeLine,
        CustomGraph,
        CustomGraphData,
        StackTraceSnapshot,
        ExceptionType,
        ExceptionMessage,
        ExceptionOccurrence,
        FunctionDefinition,
        ExceptionStackLine,
        FilePath,
        FunctionLocation,
        ExceptionFrame,
    ]
