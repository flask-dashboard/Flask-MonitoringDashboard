"""
Contains all functions that access any functionCall-object
"""

from flask import request
from sqlalchemy import func, desc
from dashboard import config
import datetime
from dashboard.database import session_scope, FunctionCall


def add_function_call(time, endpoint):
    """ Add a measurement to the database. """
    with session_scope() as db_session:
        group_by = None
        if config.get_group_by:
            group_by = config.get_group_by()

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


def get_data():
    """ Returns all data in the FunctionCall table, for the export data option. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.endpoint,
                                  FunctionCall.execution_time,
                                  FunctionCall.time,
                                  FunctionCall.version,
                                  FunctionCall.group_by,
                                  FunctionCall.ip).all()
        db_session.expunge_all()
        return result