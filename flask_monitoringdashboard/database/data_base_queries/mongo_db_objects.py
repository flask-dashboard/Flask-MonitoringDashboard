import time
import datetime
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard import config
from flask_monitoringdashboard.database.data_base_queries.query_base_object import \
    CodeLineQueriesBase, CountQueriesBase, UserQueriesBase, QueryBaseObject, \
    CustomGraphQueryBase, EndpointQueryBase, OutlierQueryBase, VersionQueryBase, \
    StackLineQueryBase, RequestQueryBase
import uuid
from pymongo import MongoClient, uri_parser
from pymongo.errors import AutoReconnect, ServerSelectionTimeoutError, DuplicateKeyError


def safe_mongo_call(call):
    def _safe_mongo_call(*args, **kwargs):
        for i in range(5):
            try:
                return call(*args, **kwargs)
            except (AutoReconnect, ServerSelectionTimeoutError):
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
        if new_content.get("monitor_level") is None:
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
        if not new_content.get("group_by"):
            new_content["group_by"] = None
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
        if not new_content.get("time_added"):
            new_content["time_added"] = datetime.datetime.utcnow()
        if not new_content.get("version_requested"):
            new_content["version_requested"] = config.version
        super().__init__(new_content)

    def create_other_indexes(self, current_collection):
        current_collection.create_index([("graph_id", 1)], unique=True, background=True)
        current_collection.create_index([("title", 1)], background=True)


class CustomGraphData(Base):
    def __init__(self, **new_content):
        new_content["__tablename__"] = '{}CustomGraphData'.format(config.table_prefix)
        if not new_content.get("id"):
            new_content["id"] = str(uuid.uuid4())
        if not new_content.get("time"):
            new_content["time"] = datetime.datetime.utcnow()
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


from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound


class CommonRouting(QueryBaseObject):
    def expunge_all(self):
        pass

    def expunge(self, obj):
        pass

    def commit(self):
        # No operation for the time being. We would need the mongodb transaction
        # but they should not be used all the time.
        # So, we skip them for the moment
        pass

    def finalize_update(self, obj):
        obj.get_collection(self.session).update_one({"id": obj.id}, {"$set": obj})

    def create_obj(self, obj):
        try:
            obj.get_collection(self.session).insert_one(obj)
        except DuplicateKeyError:
            raise IntegrityError(orig="create_obj", params="ID", statement="OBJECT ALREADY EXIST")

    @staticmethod
    def get_field_name(name, obj):
        return name

    def find_by_id(self, obj, obj_id):
        try:
            return obj(**obj().get_collection(self.session).find_one({"id": obj_id}))
        except TypeError:
            raise NoResultFound()

    def count(self, model_class):
        return model_class().get_collection(self.session).count_documents({})


class UserQueries(CommonRouting, UserQueriesBase):
    def find_one_user_or_none(self, user_id=None, username=None):
        query = {}
        if user_id:
            query["id"] = user_id
        if username:
            query["username"] = username
        if not query:
            raise ValueError()
        try:
            return User(**User().get_collection(self.session).find_one(query))
        except TypeError:
            return None

    def count_by_username(self, username):
        return User().get_collection(self.session).count_documents({"username": username})

    def get_next_id(self):
        return str(uuid.uuid4())

    def delete_user(self, user_id):
        User().get_collection(self.session).delete_one({"id": user_id})

    def delete_all_users(self):
        User().get_collection(self.session).delete_many({})

    def find_all_user(self):
        return list(User(**elem) for elem in User().get_collection(self.session).find({}).sort([("id", -1)]))


class CodeLineQueries(CommonRouting, CodeLineQueriesBase):
    def get_code_line(self, fn, ln, name, code):
        code_line_collection = CodeLine().get_collection(self.session)
        code_line_json = {
            "filename": fn,
            "line_number": ln,
            "function_name": name,
            "code": code
        }
        code_line = code_line_collection.find_one(code_line_json)
        if not code_line:
            new_code_line = CodeLine(**code_line_json)
            code_line_collection.insert_one(new_code_line)
        else:
            new_code_line = CodeLine(**code_line)
        return new_code_line


class CountQueries(CommonRouting, CountQueriesBase):
    def count_rows(self, column, *criterion):
        return len(Request().get_collection(self.session).distinct(column,
                                                                   {"$and": list(criterion)}
                                                                   if len(criterion) > 0 else {}))

    def count_requests(self, endpoint_id, *where):
        return self.count_rows("id",
                               {"endpoint_id": endpoint_id},
                               *where)

    def count_total_requests(self, *where):
        return self.count_rows("id",
                               *where)

    def count_outliers(self, endpoint_id):
        return Outlier().get_collection(self.session).count_documents({"endpoint_id": endpoint_id})

    def count_profiled_requests(self, endpoint_id):
        return len(StackLine().get_collection(self.session).distinct("request_id", {"endpoint_id": endpoint_id}))

    def count_request_per_endpoint(self, *criterion):
        query = [
            {"$group": {
                "_id": "$endpoint_id",
                "counting": {"$sum": 1}
            }}
        ]
        if len(criterion) > 0:
            query.insert(0, {"$match": {"$and": list(criterion)}})
        return list((elem["_id"], elem["counting"]) for elem in
                    Request().get_collection(self.session).aggregate(query))

    @staticmethod
    def generate_time_query(dt_begin, dt_end):
        return [{"$and": [{"time_requested": {"$gte": dt_begin}}, {"time_requested": {"$lt": dt_end}}]}]

    def get_data_grouped(self, column, *where):
        return list((elem[column], elem["duration"])
                    for elem in Request().get_collection(self.session).find({"$and": list(where)}
                                                                            if len(where) > 0
                                                                            else {}).sort([(column, 1)]))

    def get_two_columns_grouped(self, column, *where):
        return list(((elem[column], elem["version_requested"]), elem["duration"]) for elem in
                    Request().get_collection(self.session).find({"$and": list(where)}).sort([(column, 1)]))


class CustomGraphQuery(CommonRouting, CustomGraphQueryBase):
    def find_or_create_graph(self, name):
        collection = CustomGraph().get_collection(self.session)
        result = collection.find_one({
            "title": name
        })
        if not result:
            result = CustomGraph(title=name)
            collection.insert_one(result)
        return CustomGraph(**result)

    def get_graphs(self):
        return list(CustomGraph(**elem) for elem in CustomGraph().get_collection(self.session).find({}))

    def get_graph_data(self, graph_id, start_date, end_date):
        rows = list(CustomGraphData(**elem) for elem in CustomGraphData().get_collection(self.session).find({
            "graph_id": graph_id,
            "$and": [{"time": {"$gte": start_date}}, {"time": {"$lt": end_date + datetime.timedelta(days=1)}}]
        }))
        return [row2dict(row) for row in rows]


class EndpointQuery(CommonRouting, EndpointQueryBase):
    def get_num_requests(self, endpoint_id, start_date, end_date):
        query = {
            "$and": [{"time_requested": {"$gte": start_date}}, {"time_requested": {"$lte": end_date}}]
        }
        if endpoint_id:
            query["endpoint_id"] = endpoint_id
        return list(r["time_requested"] for r in Request().get_collection(self.session).find(query))

    def get_statistics(self, endpoint_id, field_name, limit):
        query = [
            {"$match": {"endpoint_id": endpoint_id}},
            {"$group": {"_id": f"${field_name}", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ]
        if limit:
            query.append({"$limit": int(limit)})
        results = Request().get_collection(self.session).aggregate(query)
        return [(result["_id"], result["counting"]) for result in results]

    def get_endpoint_or_create(self, endpoint_name):
        current_endpoint = Endpoint(name=endpoint_name)
        endpoint_collection = current_endpoint.get_collection(self.session)
        result = endpoint_collection.find_one({"name": endpoint_name})
        if not result:
            endpoint_collection.insert_one(current_endpoint)
            result = current_endpoint
        else:
            result = Endpoint(**result)
            result.time_added = to_local_datetime(result.time_added)
            result.last_requested = to_local_datetime(result.last_requested)
        return result

    def update_endpoint(self, endpoint_name, field_name, value):
        Endpoint().get_collection(self.session).update_one({"name": endpoint_name}, {"$set": {field_name: value}})

    def get_last_requested(self):
        return list((elem["name"], elem.get("last_requested")) for elem in
                    Endpoint().get_collection(self.session).find())

    def get_endpoints(self):
        endpoint_collection = Endpoint().get_collection(self.session)
        endpoints = {endpoint["id"]: endpoint for endpoint in endpoint_collection.find({})}
        endpoint_keys = list(endpoints.keys())
        request_collection = Request().get_collection(self.session)
        results = request_collection.aggregate([
            {"$match": {"endpoint_id": {"$in": endpoint_keys}}},
            {"$group": {"_id": "$endpoint_id", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ])
        output = []
        for result in results:
            output.append(Endpoint(**endpoints[result["_id"]]))
            endpoint_keys.remove(result["_id"])
        for endpoint_key in endpoint_keys:
            output.append(Endpoint(**endpoints[endpoint_key]))
        return output

    def get_endpoints_hits(self):
        endpoint_collection = Endpoint().get_collection(self.session)
        endpoints = {endpoint["id"]: endpoint["name"] for endpoint in endpoint_collection.find({})}
        request_collection = Request().get_collection(self.session)
        results = request_collection.aggregate([
            {"$match": {"endpoint_id": {"$in": list(endpoints.keys())}}},
            {"$group": {"_id": "$endpoint_id", "counting": {"$sum": 1}}},
            {"$sort": {"counting": -1}}
        ])
        return [(endpoints[result["_id"]], result["counting"]) for result in results]

    def get_avg_duration(self, endpoint_id):
        request_collection = Request().get_collection(self.session)
        results = list(request_collection.aggregate([
            {"$match": {"endpoint_id": endpoint_id}},
            {"$group": {"_id": "$endpoint_id", "average": {"$avg": "$duration"}}}
        ]))
        try:
            return results[0]["average"]
        except (TypeError, IndexError, KeyError):
            return 0

    def get_endpoint_averages(self):
        endpoint_collection = Endpoint().get_collection(self.session)
        endpoints = {endpoint["id"]: endpoint["name"] for endpoint in endpoint_collection.find({})}
        request_collection = Request().get_collection(self.session)
        results = request_collection.aggregate([
            {"$match": {"endpoint_id": {"$in": list(endpoints.keys())}}},
            {"$group": {"_id": "$endpoint_id", "average": {"$avg": "$duration"}}}
        ])
        return [(endpoints[result["_id"]], result["average"]) for result in results]

    @staticmethod
    def generate_request_error_hits_criterion():
        return {
            "$and": [{"status_code": {"$gte": 400}}, {"status_code": {"$lt": 600}}]
        }

    @staticmethod
    def filter_by_endpoint_id(endpoint_id):
        return {"endpoint_id": endpoint_id}

    @staticmethod
    def filter_by_time(current_time, hits_criterion=None):
        return {
            "$and": [{"time_requested": {"$gte": current_time}}, hits_criterion] if hits_criterion else
            [{"time_requested": {"$gte": current_time}}]
        }


class OutlierQuery(CommonRouting, OutlierQueryBase):
    def create_outlier_record(self, outlier):
        outlier.endpoint_id = Request().get_collection(self.session).find_one({
            "id": outlier.request_id
        })["endpoint_id"]
        outlier.get_collection(self.session).insert_one(outlier)

    def get_outliers_sorted(self, endpoint_id, offset, per_page):
        requests = list(Request().get_collection(self.session).find({
            "endpoint_id": endpoint_id
        }).sort([("time_requested", 1)]))
        outliers = dict()
        for elem in Outlier().get_collection(self.session).find({"endpoint_id": endpoint_id}).skip(int(offset)).limit(
                int(per_page)):
            outliers.setdefault(elem["request_id"], []).append(Outlier(**elem))
        results = []
        for request in requests:
            if outliers.get(request["id"]):
                for current_outlier in outliers[request["id"]]:
                    current_outlier["request"] = Request(**request)
                results.extend(outliers[request["id"]])
            if len(results) > int(per_page):
                break
        return results

    def get_outliers_cpus(self, endpoint_id):
        return list(elem.get("cpu_percent") for elem in
                    Outlier().get_collection(self.session).find({"endpoint_id": endpoint_id}))

    def find_by_request_id(self, request_id):
        return Outlier().get_collection(self.session).find_one({"request_id": request_id})


class VersionQuery(CommonRouting, VersionQueryBase):
    @staticmethod
    def get_version_requested_query(v):
        return {"version_requested": v}

    def get_versions(self, endpoint_id=None, limit=None):
        query = [
            {"$group": {
                "_id": "$version_requested",
                "minTime": {"$min": "$time_requested"}
            }},
            {"$sort": {"minTime": -1}}
        ]
        if endpoint_id:
            query.insert(0, {"$match": {"endpoint_id": endpoint_id}})
        if limit:
            query.append({"$limit": int(limit)})
        return list((str(elem["_id"]), elem["minTime"]) for elem in
                    Request().get_collection(self.session).aggregate(query))

    @staticmethod
    def get_2d_version_data_filter(endpoint_id):
        return {"endpoint_id": endpoint_id}

    def get_first_requests(self, endpoint_id, limit=None):
        query = [
            {"$match": {"endpoint_id": endpoint_id}},
            {"$group": {
                "_id": "$version_requested",
                "minTime": {"$min": "$time_requested"}
            }},
            {"$sort": {"minTime": -1}}
        ]
        if limit:
            query.append({"$limit": int(limit)})
        return list((elem["_id"], elem["minTime"]) for elem in Request().get_collection(self.session).aggregate(query))


class StackLineQuery(CommonRouting, StackLineQueryBase):
    def create_stack_line(self, new_stack_line):
        new_stack_line.endpoint_id = Request().get_collection(self.session).find_one({
            "id": new_stack_line.request_id
        })["endpoint_id"]
        new_stack_line.get_collection(self.session).insert_one(new_stack_line)

    def get_profiled_requests(self, endpoint_id, offset, per_page):
        requests = list(Request().get_collection(self.session).find({
            "endpoint_id": endpoint_id
        }).sort([("time_requested", 1)]))
        if not requests:
            return []
        stack_line_list = StackLine().get_collection(self.session).find({"endpoint_id": endpoint_id})
        if not stack_line_list:
            return []
        stack_lines = dict()
        code_line_ids = []
        for elem in stack_line_list:
            if elem.get("code_id"):
                code_line_ids.append(elem["code_id"])
                stack_lines.setdefault(elem["request_id"], []).append(StackLine(**elem))
        code_lines = {elem["id"]: CodeLine(**elem) for elem in
                      CodeLine().get_collection(self.session).find({"id": {"$in": code_line_ids}})}
        results = []
        for request in requests[int(offset):]:
            for stack_line in stack_lines.get(request["id"], {}):
                if stack_line.get("code_id"):
                    # stack_lines[request["id"]].request = Request(**request)
                    stack_line["code"] = code_lines.get(stack_line["code_id"])
                    new_request = Request(**request)
                    new_request.setdefault("stack_lines", []).append(stack_line)
                    results.append(new_request)
            if len(results) > int(per_page):
                break
        return results

    def get_grouped_profiled_requests(self, endpoint_id):
        stack_lines_list = StackLine().get_collection(self.session).find(
            {"endpoint_id": endpoint_id}).limit(100).sort([("request_id", -1)])
        if not stack_lines_list:
            return []
        stack_lines = dict()
        code_line_ids = []
        for elem in stack_lines_list:
            if elem.get("code_id"):
                code_line_ids.append(elem["code_id"])
                stack_lines.setdefault(elem["request_id"], []).append(StackLine(**elem))
        code_lines = {elem["id"]: CodeLine(**elem) for elem in
                      CodeLine().get_collection(self.session).find({"id": {"$in": code_line_ids}})}
        requests = list(Request().get_collection(self.session).find({
            "id": {"$in": list(stack_lines.keys())}
        }).sort([("time_requested", 1)]))
        results = []
        for request in requests:
            for stack_line in stack_lines.get(request["id"], {}):
                if stack_line.get("code_id"):
                    # stack_lines[request["id"]].request = Request(**request)
                    stack_line["code"] = code_lines.get(stack_line["code_id"])
                    new_request = Request(**request)
                    new_request.setdefault("stack_lines", []).append(stack_line)
                    results.append(new_request)
        return results

    def find_by_request_id(self, request_id):
        return StackLine().get_collection(self.session).find_one({"request_id": request_id})


class RequestQuery(CommonRouting, RequestQueryBase):
    def get_latencies_sample(self, endpoint_id, criterion, sample_size):
        if criterion and isinstance(criterion, dict):
            criterion = [criterion]
        return list(elem.get("duration") for elem in Request().get_collection(self.session).find({
            "endpoint_id": endpoint_id,
            "$and": list(criterion)
        } if criterion and len(criterion) > 0 else {"endpoint_id": endpoint_id}).limit(int(sample_size)))

    def get_error_requests_db(self, endpoint_id, criterion):
        and_condition = [
            {"status_code": {"$ne": None}},
            {"status_code": {"$exists": True}},
            {"status_code": {"$gte": 400}},
            {"status_code": {"$lte": 599}}
        ]
        if len(criterion) > 0:
            and_condition.append({"$and": list(criterion)})
        return list(Request(**elem) for elem in Request().get_collection(self.session).find({
            "endpoint_id": endpoint_id,
            "$and": and_condition
        }))

    def get_all_request_status_code_counts(self, endpoint_id):
        return list((elem["_id"], elem["counting"]) for elem in Request().get_collection(self.session).aggregate([
            {"$match": {
                "$and": [{"endpoint_id": endpoint_id},
                         {"status_code": {"$ne": None}},
                         {"status_code": {"$exists": True}}]
            }},
            {"$group": {
                "_id": "$status_code",
                "counting": {"$sum": 1}
            }}
        ]))

    @staticmethod
    def generate_time_query(dt_begin, dt_end):
        return [{"$and": [{"time_requested": {"$gt": dt_begin}}, {"time_requested": {"$lte": dt_end}}]}]

    @staticmethod
    def get_version_requested_query(v):
        return [{"version_requested": v}]

    def get_status_code_frequencies(self, endpoint_id, *criterion):
        and_condition = [
            {"endpoint_id": endpoint_id},
            {"status_code": {"$ne": None}},
            {"status_code": {"$exists": True}}
        ]
        if len(criterion) > 0:
            and_condition.append({"$and": list(criterion)})
        return {elem["_id"]: elem["counting"] for elem in Request().get_collection(self.session).aggregate([
            {"$match": {
                "$and": and_condition
            }},
            {"$group": {
                "_id": "$status_code",
                "counting": {"$sum": 1}
            }}
        ])}

    def get_date_of_first_request(self):
        result = Request().get_collection(self.session).find_one(sort=[("time_requested", 1)])
        return result.get("time_requested") if result else None

    def get_date_of_first_request_version(self, version):
        result = Request().get_collection(self.session).find_one({
            "version_requested": version
        }, sort=[("time_requested", 1)])
        return result.get("time_requested") if result else None

