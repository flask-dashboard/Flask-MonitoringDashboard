"""
Contains all functions that access any functionCall-object
"""

from flask import session, request
from sqlalchemy import func, desc
from dashboard import config
import datetime
from dashboard.database import session_scope, FunctionCall


def add_function_call(time, endpoint):
    """ Add a measurement to the database. """
    with session_scope() as db_session:
        group_by = None
        if config.group:
            group_by = session.get(config.group)
        ip = request.environ['REMOTE_ADDR']
        call = FunctionCall(endpoint=endpoint, execution_time=time, version=config.version,
                            time=datetime.datetime.now(), group_by=str(group_by), ip=ip)
        db_session.add(call)


def get_times():
    """ Return all entries of measurements with the average and total number of execution times. The results are 
    grouped by their endpoint. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.endpoint,
                                  func.count(FunctionCall.execution_time).label('count'),
                                  func.avg(FunctionCall.execution_time).label('average')
                                  ).group_by(FunctionCall.endpoint).order_by(desc('count')).all()
        db_session.expunge_all()
        return result
