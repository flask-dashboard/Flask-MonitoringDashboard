from flask_monitoringdashboard.database import DatabaseConnectionWrapper


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
    return DatabaseConnectionWrapper().database_connection.code_line_queries(session).get_code_line(fn, ln, name, code)
