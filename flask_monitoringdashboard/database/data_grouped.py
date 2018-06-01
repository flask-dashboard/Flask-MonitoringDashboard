from numpy import median

from flask_monitoringdashboard.database import Request, TestedEndpoints


def get_data_grouped(db_session, column, func, *where):
    """ Return the data for a specific endpoint. The result is grouped on column
    :param db_session: session for the database
    :param column: the column that is used for grouping
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    result = db_session.query(column, Request.execution_time). \
        filter(*where).order_by(column).all()
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


def get_endpoint_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(db_session, Request.endpoint, func, *where)


def get_test_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """

    result = db_session.query(TestedEndpoints.endpoint_name, TestedEndpoints.execution_time). \
        filter(*where).order_by(TestedEndpoints.execution_time).all()

    print(result)

    return group_result(result, func)


def get_version_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(db_session, Request.version, func, *where)


def get_user_data_grouped(db_session, func, *where):
    """
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    return get_data_grouped(db_session, Request.group_by, func, *where)


def get_two_columns_grouped(db_session, column, *where):
    """
    :param db_session: session for the database
    :param column: column that is used for the grouping (together with the Request.version)
    :param where: additional where clause
    """
    result = db_session.query(column, Request.version, Request.execution_time). \
        filter(*where).all()
    result = [((g, v), t) for g, v, t in result]
    return group_result(result, median)

