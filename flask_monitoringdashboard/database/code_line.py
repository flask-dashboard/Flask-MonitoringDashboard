from sqlalchemy.orm.exc import NoResultFound

from flask_monitoringdashboard.database import CodeLine


def get_code_line(db_session, fn, ln, name, code):
    """
    Get a CodeLine object from a given quadruple of fn, ln, name, code. If the CodeLine object doesn't already exist,
    a new one is created in the database.
    :param db_session: session for the database
    :param fn: filename (string)
    :param ln: line_number of the code (int)
    :param name: function name (string)
    :param code: line of code (string)
    :return: a CodeLine object
    """
    try:
        result = db_session.query(CodeLine). \
            filter(CodeLine.filename == fn, CodeLine.line_number == ln, CodeLine.function_name == name,
                   CodeLine.code == code).one()
    except NoResultFound:
        result = CodeLine(filename=fn, line_number=ln, function_name=name, code=code)
        db_session.add(result)
        db_session.flush()
    return result
