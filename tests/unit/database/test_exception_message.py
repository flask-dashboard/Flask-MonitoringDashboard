
"""
This file contains all unit tests of exception message in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_message.py')
"""
import pytest
from flask_monitoringdashboard.database import ExceptionMessage
from flask_monitoringdashboard.database.exception_message import add_exception_message

@pytest.mark.parametrize('message', ['some message'])
def test_add_exception_message(session, message):
    exception_message1_id = add_exception_message(session, message)
    exception_message_count = session.query(ExceptionMessage).count()
    exception_message2_id = add_exception_message(session, message)
    assert exception_message1_id == exception_message2_id
    assert exception_message_count == session.query(ExceptionMessage).count()

