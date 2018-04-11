from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.security import admin_secure


@blueprint.route('/settings', methods=['GET', 'POST'])
@admin_secure
def settings():
    password = 'x' * len(config.password)
    group_by = None
    try:
        group_by = config.get_group_by()
    except Exception:
        pass
    return render_template('settings.html', link=config.link, session=session, config=config, pw=password,
                           group_by=group_by)
