from flask_monitoringdashboard.database import CodeLine


def get_code_line(session, fn, ln, name, code):
    """
    Get a CodeLine object from a given quadruple of fn, ln, name, code. If the CodeLine object
    doesn't already exist, a new one is created in the database.
    :param session: session for the database
    :param fn: filename (string)
    :param ln: line_number of the code (int)
    :param name: function name (string)
    :param code: line of code (string)
    :return: a CodeLine object
    """
    result = (
        session.query(CodeLine)
        .filter(
            CodeLine.filename == fn,
            CodeLine.line_number == ln,
            CodeLine.function_name == name,
            CodeLine.code == code,
        )
        .first()
    )
    if not result:
        result = CodeLine(filename=fn, line_number=ln, function_name=name, code=code)
        session.add(result)
        session.flush()

    return result
