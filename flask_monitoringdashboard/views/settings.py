from flask import render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.security import admin_secure
from flask_monitoringdashboard.views.details.utils import get_details


@blueprint.route('/settings', methods=['GET', 'POST'])
@admin_secure
def settings():
    return render_template('settings.html', details=get_details(), config=config)


