import datetime

from flask import render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.timezone import to_local_datetime
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.core.utils import get_details


@blueprint.route('/configuration', methods=['GET', 'POST'])
@admin_secure
def configuration():
    with session_scope() as db_session:
        details = get_details(db_session)
    details['first-request'] = to_local_datetime(datetime.datetime.fromtimestamp(details['first-request']))
    details['first-request-version'] = to_local_datetime(datetime.datetime.
                                                         fromtimestamp(details['first-request-version']))
    return render_template('fmd_config.html', details=details, config=config)
