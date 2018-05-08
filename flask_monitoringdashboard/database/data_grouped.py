from flask_monitoringdashboard.database import FunctionCall


def get_data_grouped(db_session, func, *where):
    """ Return the median for a specific endpoint within a certain time interval.
    If date_from is not specified, all results are counted
    :param db_session: session for the database
    :param func: the function to reduce the data
    :param where: additional where clause
    """
    result = db_session.query(FunctionCall.endpoint, FunctionCall.execution_time). \
        filter(*where).order_by(FunctionCall.endpoint).all()
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
