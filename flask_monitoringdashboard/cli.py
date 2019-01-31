"""
Contains custom commands for the Flask-MonitoringDashboard
"""

import click
from flask.cli import with_appcontext


@click.group()
def fmd():
    pass


@fmd.command()
@with_appcontext
def init_db():
    print('Init db')
    # TODO: implement method
