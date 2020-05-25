from numpy import median

from flask_monitoringdashboard.database import Request


def get_data_grouped(session, column, func, *where):
    """ Return the data for a specific endpoint. The result is grouped on column
    :param session: session for the database
    :param column: the column that is used for grouping
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    result = session.query(column, Request.duration).filter(*where).order_by(column).all()
    # result is now a list of tuples per request.
    return group_result(result, func)


def group_result(result, func):
    """
    :param result: A list of rows from the database: e.g. [(key, data1), (key, data2)]
    :param func: the function to reduce the data e.g. func=median
    :return: the data that is reduced. e.g. [(key, (data1+data2)/2)]
    """
    data = {}
    for key, value in result:
        if key in data.keys():
            data[key].append(value)
        else:
            data[key] = [value]
    for key in data:
        data[key] = func(data[key])
    return data.items()


def group_result_endpoint(result, func):
    """
    :param result: A list of rows from the database: e.g. [(key, data1), (key, data2)]
    :param func: the function to reduce the data e.g. func=median
    :return: the data that is reduced. e.g. [(key, (data1+data2)/2)]
    """
    data = {}
    for key, value in result:
        if key.endpoint.name in data.keys():
            data[key.endpoint.name].append(value)
        else:
            data[key.endpoint.name] = [value]
    for key in data:
        data[key] = func(data[key])
    return data.items()


def get_endpoint_data_grouped(session, func, *where):
    """
    :param session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(session, Request.endpoint_id, func, *where)


def get_version_data_grouped(session, func, *where):
    """
    :param session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(session, Request.version_requested, func, *where)


def get_user_data_grouped(session, func, *where):
    """
    :param session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(session, Request.group_by, func, *where)


def get_two_columns_grouped(session, column, *where):
    """
    :param session: session for the database
    :param column: column that is used for the grouping (together with the Request.version)
    :param where: additional where clause
    """
    result = (
        session.query(column, Request.version_requested, Request.duration).filter(*where).all()
    )
    result = [((g, v), t) for g, v, t in result]
    return group_result(result, median)
