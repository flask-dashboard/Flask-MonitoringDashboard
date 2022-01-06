import uuid
from datetime import datetime, timedelta
from random import random

import factory
from pytest_factoryboy import register, LazyFixture

from flask_monitoringdashboard.core.profiler.util import PathHash
from flask_monitoringdashboard.core.profiler.util.grouped_stack_line import GroupedStackLine
from flask_monitoringdashboard.core.profiler.util.string_hash import StringHash
from flask_monitoringdashboard.database import DatabaseConnectionWrapper
from tests.fixtures.database import ModelFactory
import flask_monitoringdashboard


database_connection_wrapper = DatabaseConnectionWrapper(flask_monitoringdashboard.config)


class UserFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.user
    username = factory.LazyFunction(lambda: str(uuid.uuid4()))
    password_hash = factory.LazyFunction(lambda: str(uuid.uuid4()))
    is_admin = True

    @classmethod
    def _create(cls, model_class, password_hash=None, *args, **kwargs):
        """Override _create, because we set the password differently"""
        instance = model_class(**kwargs)
        instance.password = password_hash  # store the original password
        instance.set_password(password=password_hash)
        data_base_operation = database_connection_wrapper.database_connection.user_queries(cls._meta.sqlalchemy_session)
        data_base_operation.create_obj(instance)
        data_base_operation.commit()
        return instance


class EndpointFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.endpoint

    name = factory.LazyFunction(lambda: str(uuid.uuid4()))
    monitor_level = 1
    time_added = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(days=1))
    version_added = '1.0'
    last_requested = factory.LazyFunction(datetime.utcnow)


class RequestFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.request

    endpoint = factory.SubFactory(EndpointFactory)
    duration = factory.LazyFunction(lambda: random() * 5000)
    time_requested = factory.LazyFunction(datetime.utcnow)
    version_requested = factory.LazyFunction(lambda: str(uuid.uuid4()))
    group_by = None
    ip = factory.Faker('ipv4_private')
    status_code = 200


class OutlierFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.outlier

    request = None
    cpu_percent = None
    memory = None
    request_environment = None
    request_header = None
    request_url = None
    stacktrace = None


class CodeLineFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.code_line

    filename = 'abc.py'
    line_number = factory.LazyFunction(lambda: int(random() * 100))
    function_name = 'f'
    code = 'a=b'


class StackLineFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.stack_line

    request = None
    code = factory.SubFactory(CodeLineFactory)
    position = 0
    indent = 0
    duration = 12


class CustomGraphFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.custom_graph

    title = factory.Faker('name')
    time_added = factory.LazyFunction(datetime.utcnow)
    version_added = factory.LazyFunction(lambda: str(uuid.uuid4()))


class CustomGraphDataFactory(ModelFactory):
    class Meta:
        model = database_connection_wrapper.database_connection.custom_graph_data

    graph = factory.SubFactory(CustomGraphFactory)
    time = factory.LazyFunction(datetime.utcnow)
    value = factory.LazyFunction(random)


class GroupedStackLineFactory(factory.Factory):
    class Meta:
        model = GroupedStackLine

    indent = 0
    code = 'code'
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
        obj._string_hash = kwargs.get('_string_hash')
        return obj


register(UserFactory, 'user')
register(UserFactory, 'another_user')
register(EndpointFactory, 'endpoint')
register(RequestFactory, 'request_1')  # unfortunately, we can't use fixture name: 'request'
register(RequestFactory, 'request_2')
register(OutlierFactory, 'outlier_1', request=LazyFixture('request_1'))
register(OutlierFactory, 'outlier_2', request=LazyFixture('request_2'))
register(CodeLineFactory, 'code_line')
register(StackLineFactory, 'stack_line', request=LazyFixture('request_1'))
register(StackLineFactory, 'stack_line_2', request=LazyFixture('request_2'), indent=1)
register(CustomGraphFactory, 'custom_graph')
register(CustomGraphDataFactory, 'custom_graph_data')

register(GroupedStackLineFactory, 'grouped_stack_line')
register(StringHashFactory, 'string_hash')
register(PathHashFactory, 'path_hash')
