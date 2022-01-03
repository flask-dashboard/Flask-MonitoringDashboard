"""Creates the database.
For information about how to access the database via a session-variable, see: session_scope()
"""
import datetime
import random
import time
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_monitoringdashboard import config

if config.database_name.startswith("mongodb"):
    import uuid
    from pymongo import MongoClient, uri_parser
    from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError, DuplicateKeyError


    def safe_mongo_call(call):
        def _safe_mongo_call(*args, **kwargs):
            for i in range(5):
                try:
                    return call(*args, **kwargs)
                except (AutoReconnect, ServerSelectionTimeoutError) as error:
                    time.sleep(pow(2, i))
            else:
                raise AutoReconnect()

        return _safe_mongo_call


    class CollectionWrapper:
        def __init__(self, collection):
            self.collection = collection

        def __getattr__(self, item):
            elem = getattr(self.collection, item)
            if callable(elem):
                return safe_mongo_call(elem)


    class Base(dict):
        is_mongo_db = True

        def __init__(self, new_content=None):
            new_content.pop("_id", None)
            super().__init__()
            if new_content:
                for key, value in new_content.items():
                    self.__setitem__(key, value)

        def __setitem__(self, key, value):
            setattr(self, key, value)
            super().__setitem__(key, value)

        def __setattr__(self, key, value):
            super().__setitem__(key, value)
            super().__setattr__(key, value)

        def __getattr__(self, item):
            try:
                return super().__getitem__(item)
            except KeyError:
                return None

        def __getitem__(self, item):
            try:
                return super().__getitem__(item)
            except KeyError:
                return None

        def get_collection(self, database):
            return CollectionWrapper(database[self.__tablename__])

        def create_other_indexes(self, current_collection):
            return


    class User(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}User'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if new_content.get("is_admin") is None:
                new_content["is_admin"] = False
            super().__init__(new_content)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def create_other_indexes(self, current_collection):
            current_collection.create_index([("username", 1)], unique=True, background=True)


    class Endpoint(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}Endpoint'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if not new_content.get("monitor_level"):
                new_content["monitor_level"] = config.monitor_level
            if not new_content.get("time_added"):
                new_content["time_added"] = datetime.datetime.utcnow()
            if not new_content.get("version_added"):
                new_content["version_added"] = config.version
            if new_content.get("requests"):
                try:
                    with session_scope() as session:
                        new_object = []
                        for elem in new_content["requests"]:
                            new_object.append(Request(**elem))
                            new_object[-1].endpoint_id = new_content["id"]
                        new_object[0].get_collection(session).insert_many(new_object)
                except (KeyError, DuplicateKeyError):
                    pass
            super().__init__(new_content)

        def create_other_indexes(self, current_collection):
            current_collection.create_index([("name", 1)], unique=True, background=True)


    class Request(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}Request'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if not new_content.get("time_requested"):
                new_content["time_requested"] = datetime.datetime.utcnow()
            if not new_content.get("version_requested"):
                new_content["version_requested"] = config.version
            if new_content.get("endpoint"):
                try:
                    new_content["endpoint_id"] = new_content["endpoint"]["id"]
                    with session_scope() as session:
                        new_object = Endpoint(**new_content["endpoint"])
                        new_object.get_collection(session).insert_one(new_object)
                except (KeyError, DuplicateKeyError):
                    pass
            super().__init__(new_content)

        def create_other_indexes(self, current_collection):
            current_collection.create_index([("endpoint_id", 1)], background=True)


    class Outlier(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}Outlier'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if new_content.get("request"):
                try:
                    new_content["request_id"] = new_content["request"]["id"]
                    new_content["endpoint_id"] = new_content["request"]["endpoint_id"]
                    with session_scope() as session:
                        new_object = Request(**new_content["request"])
                        new_object.get_collection(session).insert_one(new_object)
                except (KeyError, DuplicateKeyError):
                    pass
            super().__init__(new_content)


    class CodeLine(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}CodeLine'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            super().__init__(new_content)


    class StackLine(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}StackLine'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if new_content.get("request"):
                try:
                    new_content["request_id"] = new_content["request"]["id"]
                    new_content["endpoint_id"] = new_content["request"]["endpoint_id"]
                    with session_scope() as session:
                        new_object = Request(**new_content["request"])
                        new_object.get_collection(session).insert_one(new_object)
                except (KeyError, DuplicateKeyError):
                    pass
            if new_content.get("code"):
                try:
                    new_content["code_id"] = new_content["code"]["id"]
                    with session_scope() as session:
                        new_object = CodeLine(**new_content["code"])
                        new_object.get_collection(session).insert_one(new_object)
                except (KeyError, DuplicateKeyError):
                    pass
            super().__init__(new_content)


    class CustomGraph(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}CustomGraph'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if not new_content.get("graph_id"):
                new_content["graph_id"] = str(uuid.uuid4())
            super().__init__(new_content)

        def create_other_indexes(self, current_collection):
            current_collection.create_index([("graph_id", 1)], unique=True, background=True)
            current_collection.create_index([("title", 1)], background=True)


    class CustomGraphData(Base):
        def __init__(self, **new_content):
            new_content["__tablename__"] = '{}CustomGraphData'.format(config.table_prefix)
            if not new_content.get("id"):
                new_content["id"] = str(uuid.uuid4())
            if new_content.get("graph"):
                try:
                    new_content["graph_id"] = new_content["graph"]["graph_id"]
                    with session_scope() as session:
                        new_graph = CustomGraph(**new_content["graph"])
                        new_graph.get_collection(session).insert_one(new_graph)
                except (KeyError, DuplicateKeyError):
                    pass
            super().__init__(new_content)


    def get_tables():
        return [User, Endpoint, Request, Outlier, StackLine, CodeLine, CustomGraph, CustomGraphData]


    @safe_mongo_call
    def init_database():
        for table in get_tables():
            current_table = table()
            collection = current_table.get_collection(db_connection)
            collection.drop_indexes()
            collection.create_index([("id", 1)], unique=True, background=True)
            current_table.create_other_indexes(collection)


    parsed_uri = uri_parser.parse_uri(config.database_name)
    database_name = parsed_uri["database"]
    db_connection = MongoClient(config.database_name)[database_name]
    init_database()


    @contextmanager
    def session_scope():
        """When accessing the database, use the following syntax:
        :return: the session for accessing the database.
        """
        yield db_connection


    def row2dict(row):
        d = {}
        for column in row.keys():
            d[column] = str(row[column])

        return d

else:
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

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship, scoped_session

    Base = declarative_base()

    class User(Base):
        """Table for storing user management."""

        __tablename__ = '{}User'.format(config.table_prefix)

        id = Column(Integer, primary_key=True)

        username = Column(String(250), unique=True, nullable=False)
        """Username for logging into the FMD."""

        password_hash = Column(String(128), nullable=False)
        """Hashed password."""

        is_admin = Column(Boolean, default=False)
        """False for guest permissions (only view access). True for admin permissions."""

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)


    class Endpoint(Base):
        """Table for storing information about the endpoints."""

        __tablename__ = '{}Endpoint'.format(config.table_prefix)

        id = Column(Integer, primary_key=True)

        name = Column(String(250), unique=True, nullable=False)
        """Name of the endpoint."""

        monitor_level = Column(Integer, default=config.monitor_level)
        """0 - disabled, 1 - performance, 2 - outliers, 3 - profiler + outliers"""

        time_added = Column(DateTime, default=datetime.datetime.utcnow)
        """Time when the endpoint was added."""

        version_added = Column(String(100), default=config.version)
        """Version when the endpoint was added into the DB."""

        last_requested = Column(DateTime)
        """Time when the endpoint was last requested."""


    class Request(Base):
        """Table for storing measurements of requests."""

        __tablename__ = '{}Request'.format(config.table_prefix)

        id = Column(Integer, primary_key=True)

        endpoint_id = Column(Integer, ForeignKey(Endpoint.id))
        endpoint = relationship(Endpoint, backref='requests')
        """The endpoint that handles the request."""

        duration = Column(Float, nullable=False)
        """Processing time of the request in milliseconds."""

        time_requested = Column(DateTime, default=datetime.datetime.utcnow)
        """Moment when the request was handled."""

        version_requested = Column(String(100), default=config.version)
        """Version when the request was handled."""

        group_by = Column(String(100), default=None)
        """Criteria which can be used for grouping multiple requests."""

        ip = Column(String(100), nullable=False)
        """IP address of the requester."""

        status_code = Column(Integer, nullable=True)
        """HTTP status code of the request."""

        outlier = relationship("Outlier", uselist=False, back_populates='request')


    class Outlier(Base):
        """Table for storing information about outliers."""

        __tablename__ = '{}Outlier'.format(config.table_prefix)

        id = Column(Integer, primary_key=True)

        request_id = Column(Integer, ForeignKey(Request.id))
        request = relationship(Request, back_populates='outlier')
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

        __tablename__ = '{}CodeLine'.format(config.table_prefix)

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

        __tablename__ = '{}StackLine'.format(config.table_prefix)

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

        __tablename__ = '{}CustomGraph'.format(config.table_prefix)

        graph_id = Column(Integer, primary_key=True)

        title = Column(String(250), nullable=False, unique=True)
        """Title of this graph."""

        time_added = Column(DateTime, default=datetime.datetime.utcnow)
        """When the graph was first added to the dashboard."""

        version_added = Column(String(100), default=config.version)
        """Version when the graph was added."""


    class CustomGraphData(Base):
        """Table for storing data collected by custom graphs."""

        __tablename__ = '{}CustomGraphData'.format(config.table_prefix)

        id = Column(Integer, primary_key=True)

        graph_id = Column(Integer, ForeignKey(CustomGraph.graph_id))
        graph = relationship(CustomGraph, backref="data")
        """Graph for which the data is collected."""

        time = Column(DateTime, default=datetime.datetime.utcnow)
        """Moment when the data is collected."""

        value = Column(Float)
        """Actual value that is measured."""


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
        except exc.OperationalError:
            session.rollback()
            time.sleep(0.5 + random.random())
            session.commit()
        except Exception as error:
            session.rollback()
            print('No commit has been made, due to the following error: {}'.format(error))
            raise error
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
        return [Endpoint, Request, Outlier, StackLine, CodeLine, CustomGraph, CustomGraphData]
