"""
Contains all functions that access a Host object
"""

from flask_monitoringdashboard.database import Host


def add_host(db_session, host_name: str, host_ip: str = "unknown"):
    """ Adds a host to the database. Returns the id.
    :param db_session: session for the database
    :param host_name: name of the machine or container
    :param host_ip: ip address of the machine or container
    :return the id of the host after it was stored in the database
    """
    host = Host(host_name=host_name, host_ip=host_ip)
    db_session.add(host)
    db_session.flush()
    return host.id
