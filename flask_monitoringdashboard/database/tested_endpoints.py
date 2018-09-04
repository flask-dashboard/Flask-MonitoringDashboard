from flask_monitoringdashboard.database import Endpoint, Test, TestEndpoint


def add_endpoint_hit(db_session, endpoint, time, test, version, job_id):
    """
    Adds an endpoint hit to the database.
    :param db_session: Session to connect to the db.
    :param endpoint: Name of the endpoint that was hit.
    :param time: Execution time in ms of the endpoint hit.
    :param test: Name of the test that caused the hit.
    :param version: Version of the user app in which the hit occurred.
    :param job_id: Travis job ID in which the hit occurred.
    """
    endpoint_id = db_session.query(Endpoint.id).filter(Endpoint.name == endpoint).first().id
    test_id = db_session.query(Test.id).filter(Test.name == test).first().id
    db_session.add(TestEndpoint(endpoint_id=endpoint_id, test_id=test_id, duration=time, app_version=version,
                                travis_job_id=job_id))


def get_tested_endpoint_names(db_session):
    """
    Returns the names of all of the endpoint for which test data is collected.
    :param db_session:
    :return list of strings
    """
    results = db_session.query(Endpoint.name).join(TestEndpoint.endpoint).\
        group_by(Endpoint.name).all()
    return [result[0] for result in results]
