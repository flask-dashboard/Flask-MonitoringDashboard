"""Contains custom commands for the Flask-MonitoringDashboard
For a list of all commands, open a terminal and type:

>>> flask fmd --help
"""

import click
from flask.cli import with_appcontext


@click.group()
def fmd():
    pass


@fmd.command()
@with_appcontext
def init_db():
    # Importing the database package is enough
    import flask_monitoringdashboard.database

    print('Flask-MonitoringDashboard database has been created')
