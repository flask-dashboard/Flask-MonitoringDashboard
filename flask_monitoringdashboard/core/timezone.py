import os
from hashlib import sha512

import pytz


def get_local_timezone():
    """
    :return: Local timezone as a string, which is used for pytz: http://stackoverflow.com/a/7841417
    """

    def filehash(path):
        with open(path, 'rb') as file:
            return sha512(file.read()).hexdigest()

    tzfile_digest = filehash('/etc/localtime')

    topdir = "/usr/share/zoneinfo/"
    for pathdir, dirs, files in os.walk(topdir):
        for filename in files:
            path = os.path.join(pathdir, filename)
            if filehash(path) == tzfile_digest:
                return path[len(topdir):]
    return 'UTC'


def to_local_datetime(datetime):
    """ Convert datetime (UTC) to local datetime from the configuration """
    from flask_monitoringdashboard import config

    if datetime:
        return datetime.replace(tzinfo=pytz.utc).astimezone(config.timezone)
    return None
