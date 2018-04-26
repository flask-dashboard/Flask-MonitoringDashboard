import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.core.utils import get_details


@blueprint.route('/configuration', methods=['GET', 'POST'])
@admin_secure
def configuration():
    details = get_details()
    details['first-request'] = datetime.datetime.utcfromtimestamp(details['first-request'])
    return render_template('config.html', details=details, config=config)


