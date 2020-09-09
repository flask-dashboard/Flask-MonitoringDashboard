"""
This file contains all unit tests that count a number of results in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/count.py')
"""
import pytest

from flask_monitoringdashboard.database.code_line import get_code_line


@pytest.mark.parametrize('filename', ['filename'])
@pytest.mark.parametrize('line_number', [42])
@pytest.mark.parametrize('function', ['f'])
@pytest.mark.parametrize('code', ['x = 5'])
def test_get_code_line(session, filename, line_number, function, code):
    code_line1 = get_code_line(session, filename, line_number, function, code)
    code_line2 = get_code_line(session, filename, line_number, function, code)
    assert code_line1.id == code_line2.id
    assert code_line1.function_name == code_line2.function_name
    assert code_line1.filename == code_line2.filename
    assert code_line1.line_number == code_line2.line_number
    assert code_line1.code == code_line2.code
