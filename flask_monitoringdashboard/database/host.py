"""
Contains all functions that access a Host object
"""

from flask_monitoringdashboard.database import Host

from sqlalchemy import asc
from sqlalchemy.orm.exc import NoResultFound


def add_host(db_session, host_name: str, host_ip: str = "unknown"):
    """ Adds a host to the database. Returns the id.
    :param db_session: session for the database
    :param host_name: name of the machine or container
    :param host_ip: ip address of the machine or container
    :return the id of the host after it was stored in the database
    """
    host = Host(name=host_name, ip=host_ip)
    db_session.add(host)
    db_session.flush()
    return host.id


def get_host_name_by_id(db_session, host_id: int):
    """
    Returns the Host id from a given hostname
    If the result doesn't exist in the database, None is returned.
    :param db_session: session for the database
    :param Host id: int
    :return host_name: string with the host name
    """
    try:
        result = db_session.query(Host).filter(Host.id == host_id).one()
    except NoResultFound:
        return None
    db_session.expunge(result)
    return result.name


def get_hosts(db_session):
    """
    Returns all Host objects from the database.
    :param db_session: session for the database
    :return list of Host objects
    """
    return db_session.query(Host).order_by(asc(Host.id))
