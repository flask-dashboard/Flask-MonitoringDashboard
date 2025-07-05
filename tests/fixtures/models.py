import uuid
from datetime import datetime, timedelta, timezone
from random import random

import factory
from pytest_factoryboy import register, LazyFixture

from flask_monitoringdashboard.core.profiler.util import PathHash
from flask_monitoringdashboard.core.profiler.util.grouped_stack_line import (
    GroupedStackLine,
)
from flask_monitoringdashboard.core.profiler.util.string_hash import StringHash
from flask_monitoringdashboard.database import (
    Endpoint,
    Request,
    Outlier,
    CodeLine,
    StackLine,
    CustomGraph,
    CustomGraphData,
    User,
    ExceptionOccurrence,
    ExceptionType,
    ExceptionMessage,
    ExceptionStackLine,
    StackTraceSnapshot,
    FilePath,
    FunctionDefinition,
    FunctionLocation,
    ExceptionFrame,
)
from tests.fixtures.database import ModelFactory


class UserFactory(ModelFactory):
    class Meta:
        model = User

    username = factory.LazyFunction(lambda: str(uuid.uuid4()))
    password_hash = factory.LazyFunction(lambda: str(uuid.uuid4()))
    is_admin = True

    @classmethod
    def _create(cls, model_class, password_hash=None, *args, **kwargs):
        """Override _create, because we set the password differently"""
        instance = model_class(**kwargs)
        instance.password = password_hash  # store the original password
        instance.set_password(password=password_hash)
        session = cls._meta.sqlalchemy_session
        session.add(instance)
        session.commit()
        return instance


class EndpointFactory(ModelFactory):
    class Meta:
        model = Endpoint

    name = factory.LazyFunction(lambda: str(uuid.uuid4()))
    monitor_level = 1
    time_added = factory.LazyFunction(lambda: datetime.now(timezone.utc) - timedelta(days=1))
    version_added = "1.0"
    last_requested = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class RequestFactory(ModelFactory):
    class Meta:
        model = Request

    endpoint = factory.SubFactory(EndpointFactory)
    duration = factory.LazyFunction(lambda: random() * 5000)
    time_requested = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    version_requested = factory.LazyFunction(lambda: str(uuid.uuid4()))
    group_by = None
    ip = factory.Faker("ipv4_private")
    status_code = 200


class OutlierFactory(ModelFactory):
    class Meta:
        model = Outlier

    request = None
    cpu_percent = None
    memory = None
    request_environment = None
    request_header = None
    request_url = None
    stacktrace = None


class CodeLineFactory(ModelFactory):
    class Meta:
        model = CodeLine

    filename = "abc.py"
    line_number = factory.LazyFunction(lambda: int(random() * 100))
    function_name = "f"
    code = "a=b"


class StackLineFactory(ModelFactory):
    class Meta:
        model = StackLine

    request = None
    code = factory.SubFactory(CodeLineFactory)
    position = 0
    indent = 0
    duration = 12


class CustomGraphFactory(ModelFactory):
    class Meta:
        model = CustomGraph

    title = factory.Faker("name")
    time_added = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    version_added = factory.LazyFunction(lambda: str(uuid.uuid4()))


class CustomGraphDataFactory(ModelFactory):
    class Meta:
        model = CustomGraphData

    graph = factory.SubFactory(CustomGraphFactory)
    time = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    value = factory.LazyFunction(random)


class GroupedStackLineFactory(factory.Factory):
    class Meta:
        model = GroupedStackLine

    indent = 0
    code = "code"
    values = [10, 10, 40]
    total_sum = 100
    total_hits = 6


class StringHashFactory(factory.Factory):
    class Meta:
        model = StringHash


class PathHashFactory(factory.Factory):
    class Meta:
        model = PathHash

    _string_hash = factory.SubFactory(StringHashFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class()
        obj._string_hash = kwargs.get("_string_hash")
        return obj


class ExceptionMessageFactory(ModelFactory):
    class Meta:
        model = ExceptionMessage

    message = factory.Faker("sentence")


class ExceptionTypeFactory(ModelFactory):
    class Meta:
        model = ExceptionType

    type = factory.Faker("word")

class FilePathFactory(ModelFactory):
    class Meta:
        model = FilePath

    path = factory.Faker("file_path")

class FunctionDefinitionFactory(ModelFactory):
    class Meta:
        model = FunctionDefinition

    code = "def fun(): return 0"
    code_hash = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = "fun"

class FunctionLocationFactory(ModelFactory):
    class Meta:
        model = FunctionLocation

    file_path = None
    function_definition = None
    function_start_line_number = factory.LazyFunction(lambda: int(random() * 100))

class ExceptionFrameFactory(ModelFactory):
    class Meta:
        model = ExceptionFrame

    function_location = None
    line_number = factory.LazyFunction(lambda: int(random() * 100))

class StackTraceSnapshotFactory(ModelFactory):
    class Meta:
        model = StackTraceSnapshot

    hash = factory.LazyFunction(lambda: str(uuid.uuid4()))

class ExceptionStackLineFactory(ModelFactory):
    class Meta:
        model = ExceptionStackLine

    stack_trace_snapshot = None
    exception_frame = None
    position = 0


class ExceptionOccurrenceFactory(ModelFactory):
    class Meta:
        model = ExceptionOccurrence

    request = None
    exception_msg = None
    exception_type = None
    stack_trace_snapshot = None
    is_user_captured = False


register(UserFactory, "user")
register(UserFactory, "another_user")
register(EndpointFactory, "endpoint")
register(
    RequestFactory, "request_1"
)  # unfortunately, we can't use fixture name: 'request'
register(RequestFactory, "request_2")
register(OutlierFactory, "outlier_1", request=LazyFixture("request_1"))
register(OutlierFactory, "outlier_2", request=LazyFixture("request_2"))
register(CodeLineFactory, "code_line")
register(StackLineFactory, "stack_line", request=LazyFixture("request_1"))
register(StackLineFactory, "stack_line_2", request=LazyFixture("request_2"), indent=1)
register(CustomGraphFactory, "custom_graph")
register(CustomGraphDataFactory, "custom_graph_data")

register(GroupedStackLineFactory, "grouped_stack_line")
register(StringHashFactory, "string_hash")
register(PathHashFactory, "path_hash")

register(ExceptionMessageFactory, "exception_message")
register(ExceptionTypeFactory, "exception_type")
register(FilePathFactory, "file_path")
register(FunctionDefinitionFactory, "function_definition")
register(
    FunctionLocationFactory, "function_location",
    file_path=LazyFixture("file_path"),
    function_definition=LazyFixture("function_definition"),
)
register(
    ExceptionFrameFactory, "exception_frame",
    function_location=LazyFixture("function_location"),
)
register(StackTraceSnapshotFactory, "stack_trace_snapshot")
register(
    ExceptionStackLineFactory,
    "exception_stack_line",
    stack_trace_snapshot=LazyFixture("stack_trace_snapshot"),
    exception_frame=LazyFixture("exception_frame"),
)
register(
    ExceptionOccurrenceFactory,
    "exception_occurrence",
    request=LazyFixture("request_1"),
    exception_msg=LazyFixture("exception_message"),
    exception_type=LazyFixture("exception_type"),
    stack_trace_snapshot=LazyFixture("stack_trace_snapshot"),
)
