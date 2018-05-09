from flask_monitoringdashboard.database import FunctionCall


def get_data_grouped(db_session, column, func, *where):
    """ Return the data for a specific endpoint. The result is grouped on column
    :param db_session: session for the database
    :param column: the column that is used for grouping
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    result = db_session.query(column, FunctionCall.execution_time). \
        filter(*where).order_by(column).all()
    # result is now a list of tuples per request.
    data = {}
    for key, value in result:
        if key in data.keys():
            data[key].append(value)
        else:
            data[key] = [value]
    # compute median
    for key in data:
        data[key] = func(data[key])
    return data.items()


def get_endpoint_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(db_session, FunctionCall.endpoint, func, *where)


def get_version_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(db_session, FunctionCall.version, func, *where)


def get_user_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(db_session, FunctionCall.group_by, func, *where)
