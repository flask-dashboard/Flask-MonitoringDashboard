from flask_monitoringdashboard.database import FunctionCall
from numpy import median


def get_median_group(db_session, *where):
    """ Return the median for a specific endpoint within a certain time interval.
    If date_from is not specified, all results are counted
    :param db_session: session for the database
    :param where: additional where clause
    """
    result = db_session.query(FunctionCall.endpoint, FunctionCall.execution_time). \
        filter(*where).order_by(FunctionCall.endpoint).all()
    # result is now a list of tuples per request.
    combine = {}
    for key, value in result:
        if key in combine.keys():
            combine[key].append(value)
        else:
            combine[key] = [value]
    # compute median
    for key in combine:
        combine[key] = median(combine[key])
    return combine.items()
