"""
Contains all functions that access an StackLine object.
"""

from sqlalchemy import desc, distinct
from sqlalchemy.orm import joinedload

from flask_monitoringdashboard.database import StackLine, Request, CodeLine
from flask_monitoringdashboard.database.code_line import get_code_line


def add_stack_line(session, request_id, position, indent, duration, code_line):
    """
    Adds a StackLine to the database (and possibly a CodeLine)
    :param session: Session for the database
    :param request_id: id of the request
    :param position: position of the StackLine
    :param indent: indent-value
    :param duration: duration of this line (in ms)
    :param code_line: quadruple that consists of: (filename, line_number, function_name, code)
    """
    fn, ln, name, code = code_line
    db_code_line = get_code_line(session, fn, ln, name, code)
    new_stack_line = StackLine(
        request_id=request_id,
        position=position,
        indent=indent,
        code_id=db_code_line.id,
        duration=duration,
    )
    if getattr(StackLine, "is_mongo_db", False):
        new_stack_line.endpoint_id = Request().get_collection(session).find_one({
            "id": request_id
        })["endpoint_id"]
        new_stack_line.get_collection(session).insert_one(new_stack_line)
    else:
        session.add(new_stack_line)


def get_profiled_requests(session, endpoint_id, offset, per_page):
    """
    Gets the requests of an endpoint sorted by request time, together with the stack lines.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list with tuples. Each tuple consists first of a Request-object, and the second part
    of the tuple is a list of StackLine-objects.
    """
    if getattr(StackLine, "is_mongo_db", False):
        requests = list(Request().get_collection(session).find({
            "endpoint_id": endpoint_id
        }).sort([("time_requested", 1)]))
        if not requests:
            return []
        stack_line_list = StackLine().get_collection(session).find({"endpoint_id": endpoint_id})
        if not stack_line_list:
            return []
        stack_lines = dict()
        code_line_ids = []
        for elem in stack_line_list:
            if elem.get("code_id"):
                code_line_ids.append(elem["code_id"])
                stack_lines.setdefault(elem["request_id"], []).append(StackLine(**elem))
        code_lines = {elem["id"]: CodeLine(**elem) for elem in
                      CodeLine().get_collection(session).find({"id":  {"$in": code_line_ids}})}
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
    else:
        result = (
            session.query(Request)
            .filter(Request.endpoint_id == endpoint_id)
            .options(joinedload(Request.stack_lines).joinedload(StackLine.code))
            .filter(Request.stack_lines.any())
            .order_by(desc(Request.time_requested))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        session.expunge_all()
        return result


def get_grouped_profiled_requests(session, endpoint_id):
    """
    Gets the grouped stack lines of all requests of an endpoint.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :return: A list with tuples. Each tuple consists first of a Request-object, and the second part
    of the tuple is a list of StackLine-objects.
    """
    if getattr(StackLine, "is_mongo_db", False):
        stack_lines_list = StackLine().get_collection(session).find(
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
                      CodeLine().get_collection(session).find({"id": {"$in": code_line_ids}})}
        requests = list(Request().get_collection(session).find({
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
    else:
        t = (
            session.query(distinct(StackLine.request_id).label('id'))
            .filter(Request.endpoint_id == endpoint_id)
            .join(Request.stack_lines)
            .order_by(StackLine.request_id.desc())
            .limit(100)
            .subquery('t')
        )
        # Limit the number of results by 100, otherwise the profiler gets too large
        # and the page doesn't load anymore. We show the most recent 100 requests.
        result = (
            session.query(Request)
            .join(Request.stack_lines)
            .filter(Request.id == t.c.id)
            .order_by(desc(Request.id))
            .options(joinedload(Request.stack_lines).joinedload(StackLine.code))
            .all()
        )
        session.expunge_all()
        return result
