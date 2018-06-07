from flask import request, render_template

from flask_monitoringdashboard import blueprint, user_app
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.forms import get_monitor_form
from flask_monitoringdashboard.core.info_box import get_rules_info
from flask_monitoringdashboard.core.measurement import add_decorator
from flask_monitoringdashboard.core.rules import get_rules
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count_group import get_value
from flask_monitoringdashboard.database.endpoint import get_endpoint_by_name, update_endpoint, get_last_requested


@blueprint.route('/rules', methods=['GET', 'POST'])
@admin_secure
def rules():
    """
    Renders a table with all rules from the user_app. The fmd_dashboard rules are excluded
    In case of the POST request, the data from the form is validated and processed, such that the required rules are
    monitored
    :return:
    """
    if request.method == 'POST':
        with session_scope() as db_session:
            endpoint_name = request.form['name']
            value = int(request.form['value'])
            update_endpoint(db_session, endpoint_name, value=value)

            # Remove wrapper
            original = getattr(user_app.view_functions[endpoint_name], 'original', None)
            if original:
                user_app.view_functions[endpoint_name] = original

        with session_scope() as db_session:
            add_decorator(get_endpoint_by_name(db_session, endpoint_name))

        return 'OK'

    with session_scope() as db_session:
        last_accessed = get_last_requested(db_session)
        all_rules = []
        for rule in get_rules():
            db_rule = get_endpoint_by_name(db_session, rule.endpoint)
            all_rules.append({
                'color': get_color(rule.endpoint),
                'rule': rule.rule,
                'endpoint': rule.endpoint,
                'methods': rule.methods,
                'last_accessed': get_value(last_accessed, rule.endpoint, default=None),
                'form': get_monitor_form(rule.endpoint, db_rule.monitor_level)
            })
    return render_template('fmd_rules.html', rules=all_rules, information=get_rules_info())
