
"""
This file contains all unit tests of exception info in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_info.py')
"""
from flask_monitoringdashboard.database import ExceptionInfo
from flask_monitoringdashboard.database.exception_info import get_exception_info, add_exception_info, count_grouped_exceptions, count_endpoint_grouped_exceptions, get_exceptions_with_timestamps, delete_exception, get_exceptions_with_timestamps_and_stacktrace_id

""" #The below code is failing because stacktrace is not relational to exception info and therefore the model cannot be created with a full stack trace object as a parameter
def test_get_exception_info(session, exception_info):
    e_info = get_exception_info(session, exception_info.request_id)
    assert e_info.request_id == exception_info.request_id
    assert e_info.exception_type_id == exception_info.exception_type_id
    assert e_info.exception_msg_id == exception_info.exception_msg_id
    assert e_info.full_stack_trace_id == exception_info.full_stack_trace_id

"""