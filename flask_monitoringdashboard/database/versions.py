from flask_monitoringdashboard.database import session_scope, FunctionCall


def get_date_first_request(version=None):
    """
    :param version: optional: first date when this version is requested
    :return: a datetime object with the value of when the first request is made
    """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.time).\
            filter((FunctionCall.version == version) | (version is None)).first()
        if result:
            return result[0]
        return None
