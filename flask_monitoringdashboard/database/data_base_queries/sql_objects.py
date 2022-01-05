import time
import datetime
import random
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard import config
from flask_monitoringdashboard.database.data_base_queries.query_base_object import \
    CodeLineQueriesBase, CountQueriesBase, UserQueriesBase, QueryBaseObject, \
    CustomGraphQueryBase, EndpointQueryBase, OutlierQueryBase, VersionQueryBase, \
    StackLineQueryBase, RequestQueryBase
from flask_monitoringdashboard.core.logger import log

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
    func,
    distinct,
    desc,
    and_
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, joinedload
from sqlalchemy.orm.exc import NoResultFound


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
    with session_scope() as session:
        session.query(...)
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
        log('No commit has been made, due to the following error: {}'.format(error))
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


class CommonRouting(QueryBaseObject):
    def expunge_all(self):
        self.session.expunge_all()

    def expunge(self, obj):
        self.session.expunge(obj)

    def commit(self):
        self.session.commit()

    def finalize_update(self, obj):
        # Update is done when session.commit is called
        pass

    def create_obj(self, obj):
        self.session.add(obj)

    @staticmethod
    def get_field_name(name, obj):
        return getattr(obj, name, None)

    def find_by_id(self, obj, obj_id):
        return self.session.query(obj).filter(obj.id == obj_id).one()

    def count(self, model_class):
        return self.session.query(model_class).count()


class UserQueries(CommonRouting, UserQueriesBase):
    def find_one_user_or_none(self, user_id=None, username=None):
        query = []
        if user_id:
            query.append(User.id == user_id)
        if username:
            query.append(User.username == username)
        if not query:
            raise ValueError()
        return self.session.query(User).filter(*query).one_or_none()

    def count_by_username(self, username):
        return self.session.query(User).filter(User.username == username).count()

    def delete_user(self, user_id):
        self.session.query(User).filter(User.id == user_id).delete()

    def delete_all_users(self):
        self.session.query(User).delete()

    def find_all_user(self):
        return self.session.query(User).order_by(User.id).all()

    def get_next_id(self):
        return self.session.query(User).count() + 1


class CodeLineQueries(CommonRouting, CodeLineQueriesBase):
    def get_code_line(self, fn, ln, name, code):
        result = (
            self.session.query(CodeLine)
                .filter(
                CodeLine.filename == fn,
                CodeLine.line_number == ln,
                CodeLine.function_name == name,
                CodeLine.code == code,
            )
                .first()
        )
        if not result:
            result = CodeLine(filename=fn, line_number=ln, function_name=name, code=code)
            self.session.add(result)
            self.session.flush()

        return result


class CountQueries(CommonRouting, CountQueriesBase):
    def count_rows(self, column, *criterion):
        return self.session.query(func.count(distinct(column))).filter(*criterion).scalar()

    def count_requests(self, endpoint_id, *where):
        return self.count_rows(Request.id,
                               Request.endpoint_id == endpoint_id,
                               *where)

    def count_total_requests(self, *where):
        return self.count_rows(Request.id,
                               *where)

    def count_outliers(self, endpoint_id):
        return self.count_rows(Request.id,
                               Request.endpoint_id == endpoint_id,
                               Request.outlier)

    def count_profiled_requests(self, endpoint_id):
        return (
            self.session.query(func.count(distinct(StackLine.request_id)))
            .filter(Request.endpoint_id == endpoint_id)
            .join(Request.stack_lines)
            .scalar()
        )

    def count_request_per_endpoint(self, *criterion):
        return (
            self.session.query(Request.endpoint_id, func.count(Request.id))
            .filter(*criterion)
            .group_by(Request.endpoint_id)
            .all()
        )

    @staticmethod
    def generate_time_query(dt_begin, dt_end):
        return [Request.time_requested >= dt_begin, Request.time_requested < dt_end]

    def get_data_grouped(self, column, *where):
        return self.session.query(column, Request.duration).filter(*where).order_by(column).all()

    def get_two_columns_grouped(self, column, *where):
        result = (
            self.session.query(column, Request.version_requested, Request.duration).filter(*where).all()
        )
        return [((g, v), t) for g, v, t in result]


class CustomGraphQuery(CommonRouting, CustomGraphQueryBase):
    def find_or_create_graph(self, name):
        try:
            result = self.session.query(CustomGraph).filter(CustomGraph.title == name).one()
        except NoResultFound:
            result = CustomGraph(title=name)
            self.session.add(result)
            self.session.flush()
        self.session.expunge(result)
        return result

    def get_graphs(self):
        try:
            return self.session.query(CustomGraph).all()
        finally:
            self.session.expunge_all()

    def get_graph_data(self, graph_id, start_date, end_date):
        rows = self.session.query(CustomGraphData).filter(
            CustomGraphData.graph_id == graph_id,
            CustomGraphData.time >= start_date,
            CustomGraphData.time < end_date + datetime.timedelta(days=1),
        ).all()
        return [row2dict(row) for row in rows]


class EndpointQuery(CommonRouting, EndpointQueryBase):
    def get_num_requests(self, endpoint_id, start_date, end_date):
        query = self.session.query(Request.time_requested)
        if endpoint_id:
            query = query.filter(Request.endpoint_id == endpoint_id)
        result = query.filter(
            Request.time_requested >= start_date, Request.time_requested <= end_date
        ).all()

        return [r[0] for r in result]

    def get_statistics(self, endpoint_id, field_name, limit):
        query = (
            self.session.query(field_name, func.count(field_name)).
            filter(Request.endpoint_id == endpoint_id).
            group_by(field_name).
            order_by(desc(func.count(field_name)))
        )
        if limit:
            query = query.limit(limit)
        result = query.all()
        self.session.expunge_all()
        return result

    def get_endpoint_or_create(self, endpoint_name):
        try:
            result = self.session.query(Endpoint).filter(Endpoint.name == endpoint_name).one()
            result.time_added = to_local_datetime(result.time_added)
            result.last_requested = to_local_datetime(result.last_requested)
        except NoResultFound:
            result = Endpoint(name=endpoint_name)
            self.session.add(result)
            self.session.flush()
        self.session.expunge(result)
        return result

    def update_endpoint(self, endpoint_name, field_name, value):
        self.session.query(Endpoint).filter(Endpoint.name == endpoint_name).update(
            {field_name: value}
        )
        self.session.flush()

    def get_last_requested(self):
        result = self.session.query(Endpoint.name, Endpoint.last_requested).all()
        self.session.expunge_all()
        return result

    def get_endpoints(self):
        return (
            self.session.query(Endpoint)
                .outerjoin(Request)
                .group_by(Endpoint.id)
                .order_by(desc(func.count(Request.endpoint_id)))
        )

    def get_endpoints_hits(self):
        return (
            self.session.query(Endpoint.name, func.count(Request.endpoint_id))
                .join(Request)
                .group_by(Endpoint.name)
                .order_by(desc(func.count(Request.endpoint_id)))
                .all()
        )

    def get_avg_duration(self, endpoint_id):
        result = (
            self.session.query(func.avg(Request.duration).label('average'))
            .filter(Request.endpoint_id == endpoint_id)
            .one()
        )
        return result[0] if result[0] else 0

    def get_endpoint_averages(self):
        result = (
            self.session.query(Endpoint.name, func.avg(Request.duration).label('average'))
                .outerjoin(Request)
                .group_by(Endpoint.name)
                .all()
        )
        return result

    @staticmethod
    def generate_request_error_hits_criterion():
        return and_(Request.status_code >= 400, Request.status_code < 600)

    @staticmethod
    def filter_by_endpoint_id(endpoint_id):
        return Request.endpoint_id == endpoint_id

    @staticmethod
    def filter_by_time(current_time, hits_criterion=None):
        if hits_criterion is None:
            return Request.time_requested > current_time
        else:
            return and_(Request.time_requested > current_time, hits_criterion)


class OutlierQuery(CommonRouting, OutlierQueryBase):
    def create_outlier_record(self, outlier):
        self.session.add(outlier)

    def get_outliers_sorted(self, endpoint_id, offset, per_page):
        result = (
            self.session.query(Outlier)
            .join(Outlier.request)
            .options(joinedload(Outlier.request).joinedload(Request.endpoint))
            .filter(Request.endpoint_id == endpoint_id)
            .order_by(desc(Request.time_requested))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        self.session.expunge_all()
        return result

    def get_outliers_cpus(self, endpoint_id):
        outliers = (
            self.session.query(Outlier.cpu_percent)
            .join(Outlier.request)
            .filter(Request.endpoint_id == endpoint_id)
            .all()
        )
        return [outlier[0] for outlier in outliers]

    def find_by_request_id(self, request_id):
        return self.session.query(Outlier).filter(Outlier.request_id == request_id).one()


class VersionQuery(CommonRouting, VersionQueryBase):
    @staticmethod
    def get_version_requested_query(v):
        return Request.version_requested == v

    def get_versions(self, endpoint_id=None, limit=None):
        query = self.session.query(Request.version_requested, func.min(Request.time_requested))
        if endpoint_id:
            query = query.filter(Request.endpoint_id == endpoint_id)
        query = query.group_by(Request.version_requested)
        query = query.order_by(func.min(Request.time_requested).desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_2d_version_data_filter(endpoint_id):
        return Request.endpoint_id == endpoint_id

    def get_first_requests(self, endpoint_id, limit=None):
        query = (
            self.session.query(
                Request.version_requested, func.min(Request.time_requested).label('first_used')
            )
                .filter(Request.endpoint_id == endpoint_id)
                .group_by(Request.version_requested)
                .order_by(desc('first_used'))
        )
        if limit:
            query = query.limit(limit)
        return query.all()


class StackLineQuery(CommonRouting, StackLineQueryBase):
    def create_stack_line(self, new_stack_line):
        self.session.add(new_stack_line)

    def get_profiled_requests(self, endpoint_id, offset, per_page):
        result = (
            self.session.query(Request)
                .filter(Request.endpoint_id == endpoint_id)
                .options(joinedload(Request.stack_lines).joinedload(StackLine.code))
                .filter(Request.stack_lines.any())
                .order_by(desc(Request.time_requested))
                .offset(offset)
                .limit(per_page)
                .all()
        )
        self.session.expunge_all()
        return result

    def get_grouped_profiled_requests(self, endpoint_id):
        t = (
            self.session.query(distinct(StackLine.request_id).label('id'))
            .filter(Request.endpoint_id == endpoint_id)
            .join(Request.stack_lines)
            .order_by(StackLine.request_id.desc())
            .limit(100)
            .subquery('t')
        )
        # Limit the number of results by 100, otherwise the profiler gets too large
        # and the page doesn't load anymore. We show the most recent 100 requests.
        result = (
            self.session.query(Request)
            .join(Request.stack_lines)
            .filter(Request.id == t.c.id)
            .order_by(desc(Request.id))
            .options(joinedload(Request.stack_lines).joinedload(StackLine.code))
            .all()
        )
        self.session.expunge_all()
        return result

    def find_by_request_id(self, request_id):
        return self.session.query(StackLine).filter(StackLine.request_id == request_id).one_or_none()


class RequestQuery(CommonRouting, RequestQueryBase):
    def get_latencies_sample(self, endpoint_id, criterion, sample_size):
        query = (
            self.session.query(Request.duration).filter(Request.endpoint_id == endpoint_id, *criterion)
        )
        # return random rows: See https://stackoverflow.com/a/60815
        dialect = self.session.bind.dialect.name

        if dialect == 'sqlite':
            query = query.order_by(func.random())
        elif dialect == 'mysql':
            query = query.order_by(func.rand())

        query = query.limit(sample_size)

        return [item.duration for item in query.all()]

    def get_error_requests_db(self, endpoint_id, criterion):
        criteria = and_(
            Request.endpoint_id == endpoint_id,
            Request.status_code.isnot(None),
            Request.status_code >= 400,
            Request.status_code <= 599,
        )
        return self.session.query(Request).filter(criteria, *criterion).all()

    def get_all_request_status_code_counts(self, endpoint_id):
        return (
            self.session.query(Request.status_code, func.count(Request.status_code))
                .filter(Request.endpoint_id == endpoint_id, Request.status_code.isnot(None))
                .group_by(Request.status_code)
                .all()
        )

    @staticmethod
    def generate_time_query(dt_begin, dt_end):
        return and_(Request.time_requested > dt_begin, Request.time_requested <= dt_end)

    @staticmethod
    def get_version_requested_query(v):
        return Request.version_requested == v

    def get_status_code_frequencies(self, endpoint_id, *criterion):
        status_code_counts = self.session.query(Request.status_code, func.count(Request.status_code)) \
            .filter(Request.endpoint_id == endpoint_id, Request.status_code.isnot(None), *criterion) \
            .group_by(Request.status_code).all()
        return dict(status_code_counts)

    def get_date_of_first_request(self):
        result = self.session.query(Request.time_requested).order_by(Request.time_requested).first()
        return result[0] if result else None

    def get_date_of_first_request_version(self, version):
        result = (
            self.session.query(Request.time_requested)
                .filter(Request.version_requested == version)
                .order_by(Request.time_requested)
                .first()
        )
        return result[0] if result else None
