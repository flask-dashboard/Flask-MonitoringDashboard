from flask_monitoringdashboard.database import TestedEndpoints


def add_endpoint_hit(db_session, endpoint, time, test, version, job_id):
    """
    Adds an endpoint hit to the database.
    :param db_session: Session to conect to the db.
    :param endpoint: Name of the endpoint that was hit.
    :param time: Execution time in ms of the endpoint hit.
    :param test: Name of the test that caused the hit.
    :param version: Version of the user app in which the hit occurred.
    :param job_id: Travis job ID in which the hit occurred.
    :return:
    """
    db_session.add(TestedEndpoints(endpoint_name=endpoint, execution_time=time, test_name=test, app_version=version,
                                   travis_job_id=job_id))
