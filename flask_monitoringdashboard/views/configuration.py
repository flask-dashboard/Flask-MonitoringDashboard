import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.core.utils import get_details


@blueprint.route('/configuration', methods=['GET', 'POST'])
@admin_secure
def configuration():
    with session_scope() as db_session:
        details = get_details(db_session)
    details['first-request'] = datetime.datetime.utcfromtimestamp(details['first-request'])
    return render_template('fmd_config.html', details=details, config=config)


