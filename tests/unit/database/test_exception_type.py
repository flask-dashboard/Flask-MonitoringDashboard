
"""
This file contains all unit tests of exception type in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_type.py')
"""
import pytest
from flask_monitoringdashboard.database import ExceptionType
from flask_monitoringdashboard.database.exception_type import add_exception_type


@pytest.mark.parametrize('type', ['type'])
def test_add_exception_message(session, type):
    exception_type1_id = add_exception_type(session, type)
    exception_type_count = session.query(ExceptionType).count()
    exception_type2_id = add_exception_type(session, type)
    assert exception_type1_id == exception_type2_id
    assert exception_type_count == session.query(ExceptionType).count()
