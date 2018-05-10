from flask import request, render_template

from flask_monitoringdashboard import blueprint, user_app
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.measurement import track_performance
from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times


@blueprint.route('/rules', methods=['GET', 'POST'])
@admin_secure
def rules():
    """
    Renders a table with all rules from the user_app. The fmd_dashboard rules are excluded
    In case of the POST request, the data from the form is validated and processed, such that the required rules are
    monitored
    :return:
    """
    with session_scope() as db_session:
        if request.method == 'POST':
            name = request.form['name']
            endpoint = name.rsplit('-', 1)[1]
            value = request.form['value']

            if value == 'true':  # add wrapper
                update_monitor_rule(db_session, endpoint, value=True)
                user_app.view_functions[endpoint] = track_performance(user_app.view_functions[endpoint], endpoint)
            else:  # remove wrapper
                update_monitor_rule(db_session, endpoint, value=False)
                original = getattr(user_app.view_functions[endpoint], 'original', None)
                if original:
                    user_app.view_functions[endpoint] = original
            return 'OK'

        last_accessed = get_last_accessed_times(db_session)
        all_rules = [{
            'color': get_color(rule.endpoint),
            'rule': rule.rule,
            'endpoint': rule.endpoint,
            'methods': rule.methods,
            'last_accessed': get_value(last_accessed, rule.endpoint, default=None),
            'monitor': get_monitor_rule(db_session, rule.endpoint).monitor
        } for rule in get_rules()]
    return render_template('fmd_rules.html', rules=all_rules)
