from abc import ABC, abstractmethod


class DatabaseConnectionBase(ABC):
    def __init__(self):
        self.db_connection = None

    @property
    @abstractmethod
    def user_queries(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def endpoint_query(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def request_query(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def outlier_query(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def code_line_queries(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def stack_line_query(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def custom_graph_query(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def count_queries(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def version_query(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def user(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def endpoint(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def request(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def outlier(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def code_line(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def stack_line(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def custom_graph(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def custom_graph_data(self):
        raise NotImplementedError()

    def init_database(self):
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()

    def session_scope(self):
        raise NotImplementedError()

    @staticmethod
    def row2dict(row):
        raise NotImplementedError()

    @staticmethod
    def get_tables():
        raise NotImplementedError()


class QueryBaseObject(ABC):
    def __init__(self, session):
        self.session = session

    def commit(self):
        raise NotImplementedError()

    def expunge_all(self):
        raise NotImplementedError()

    def expunge(self, obj):
        raise NotImplementedError()

    def finalize_update(self, obj):
        raise NotImplementedError()

    def create_obj(self, obj):
        raise NotImplementedError()

    @staticmethod
    def get_field_name(name, obj):
        raise NotImplementedError()

    def find_by_id(self, obj, obj_id):
        raise NotImplementedError()

    def count(self, model_class):
        raise NotImplementedError()


class UserQueriesBase(QueryBaseObject, ABC):
    def find_one_user_or_none(self, user_id=None, username=None):
        raise NotImplementedError()

    def delete_user(self, user_id):
        raise NotImplementedError()

    def find_all_user(self):
        raise NotImplementedError()

    def count_by_username(self, username):
        raise NotImplementedError()

    def get_next_id(self):
        raise NotImplementedError()

    def delete_all_users(self):
        raise NotImplementedError()


class CodeLineQueriesBase(QueryBaseObject, ABC):
    def get_code_line(self, fn, ln, name, code):
        raise NotImplementedError()


class CountQueriesBase(QueryBaseObject, ABC):
    def count_rows(self, column, *criterion):
        raise NotImplementedError()

    def count_requests(self, endpoint_id, *where):
        raise NotImplementedError()

    def count_total_requests(self, *where):
        raise NotImplementedError()

    def count_outliers(self, endpoint_id):
        raise NotImplementedError()

    def count_profiled_requests(self, endpoint_id):
        raise NotImplementedError()

    def count_request_per_endpoint(self, column, *criterion):
        raise NotImplementedError()

    @staticmethod
    def generate_time_query(dt_begin, dt_end):
        raise NotImplementedError()

    def get_data_grouped(self, column, *where):
        raise NotImplementedError()

    def get_two_columns_grouped(self, column, *where):
        raise NotImplementedError()


class CustomGraphQueryBase(QueryBaseObject, ABC):
    def find_or_create_graph(self, name):
        raise NotImplementedError

    def get_graphs(self):
        raise NotImplementedError()

    def get_graph_data(self, graph_id, start_date, end_date):
        raise NotImplementedError()


class EndpointQueryBase(QueryBaseObject, ABC):
    def get_num_requests(self, endpoint_id, start_date, end_date):
        raise NotImplementedError()

    def get_statistics(self, endpoint_id, field_name, limit):
        raise NotImplementedError()

    def get_endpoint_or_create(self, endpoint_name):
        raise NotImplementedError()

    def update_endpoint(self, endpoint_name, field_name, value):
        raise NotImplementedError()

    def get_last_requested(self):
        raise NotImplementedError()

    def get_endpoints(self):
        raise NotImplementedError()

    def get_endpoints_hits(self):
        raise NotImplementedError()

    def get_avg_duration(self, endpoint_id):
        raise NotImplementedError()

    def get_endpoint_averages(self):
        raise NotImplementedError()

    @staticmethod
    def generate_request_error_hits_criterion():
        raise NotImplementedError()

    @staticmethod
    def filter_by_endpoint_id(endpoint_id):
        raise NotImplementedError()

    @staticmethod
    def filter_by_time(current_time, hits_criterion=None):
        raise NotImplementedError()


class OutlierQueryBase(QueryBaseObject, ABC):
    def create_outlier_record(self, obj):
        raise NotImplementedError()

    def get_outliers_sorted(self, endpoint_id, offset, per_page):
        raise NotImplementedError()

    def get_outliers_cpus(self, endpoint_id):
        raise NotImplementedError()

    def find_by_request_id(self, request_if):
        raise NotImplementedError()


class VersionQueryBase(QueryBaseObject, ABC):
    @staticmethod
    def get_version_requested_query(v):
        raise NotImplementedError()

    def get_versions(self, endpoint_id=None, limit=None):
        raise NotImplementedError()

    @staticmethod
    def get_2d_version_data_filter(endpoint_id):
        raise NotImplementedError()

    def get_first_requests(self, endpoint_id, limit=None):
        raise NotImplementedError()


class StackLineQueryBase(QueryBaseObject, ABC):
    def create_stack_line(self, stack_line):
        raise NotImplementedError()

    def get_profiled_requests(self, endpoint_id, offset, per_page):
        raise NotImplementedError()

    def get_grouped_profiled_requests(self, endpoint_id):
        raise NotImplementedError()

    def find_by_request_id(self, request_id):
        raise NotImplementedError()


class RequestQueryBase(QueryBaseObject, ABC):
    def get_latencies_sample(self, endpoint_id, criterion, sample_size):
        raise NotImplementedError()

    def get_error_requests_db(self, endpoint_id, criterion):
        raise NotImplementedError()

    def get_all_request_status_code_counts(self, endpoint_id):
        raise NotImplementedError()

    @staticmethod
    def generate_time_query(dt_begin, dt_end):
        raise NotImplementedError()

    @staticmethod
    def get_version_requested_query(v):
        raise NotImplementedError()

    def get_status_code_frequencies(self, endpoint_id, *criterion):
        raise NotImplementedError()

    def get_date_of_first_request(self):
        raise NotImplementedError()

    def get_date_of_first_request_version(self, version):
        raise NotImplementedError()


