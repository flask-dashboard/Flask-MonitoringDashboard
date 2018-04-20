from flask import request, render_template

from flask_monitoringdashboard import blueprint, config, user_app
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.auth import admin_secure
from flask_monitoringdashboard.core.forms import MonitorDashboard
from flask_monitoringdashboard.core.measurement import track_performance
from flask_monitoringdashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times
from flask_monitoringdashboard.database.monitor_rules import reset_monitor_endpoints


@blueprint.route('/rules', methods=['GET', 'POST'])
@admin_secure
def rules():
    """
    Renders a table with all rules from the user_app. The dashboard rules are excluded
    In case of the POST request, the data from the form is validated and processed, such that the required rules are
    monitored
    :return:
    """
    form = MonitorDashboard(request.form)

    if request.method == 'POST' and form.validate():
        # Remove the monitor endpoints from the database
        reset_monitor_endpoints()

        for rule in get_app_rules():
            # Remove existing wrappers
            original = getattr(user_app.view_functions[rule.endpoint], 'original', None)
            if original:
                user_app.view_functions[rule.endpoint] = original

        # request.form only contains checkboxes that are checked
        for data in request.form:
            if data.startswith('checkbox-'):
                endpoint = data.rsplit('-', 1)[1]
                update_monitor_rule(endpoint, value=True)
                rule = get_monitor_rule(endpoint)
                # Add wrappers to the existing functions
                user_app.view_functions[rule.endpoint] = track_performance(user_app.view_functions[rule.endpoint],
                                                                           rule.endpoint)
    all_rules = []
    for rule in get_app_rules():
        all_rules.append({
            'color': get_color(rule.endpoint),
            'rule': rule.rule,
            'endpoint': rule.endpoint,
            'methods': rule.methods,
            'last_accessed': get_last_accessed_times(rule.endpoint),
            'monitor': get_monitor_rule(rule.endpoint).monitor
        })

    return render_template('rules.html', rules=all_rules, form=form)


def get_app_rules():
    """
    :return: A list with all rules that are currently present in the user_app. The Dashboard-rules are excluded
    """
    all_rules = user_app.url_map.iter_rules()
    return [r for r in all_rules if not r.rule.startswith('/' + config.link)
            and not r.rule.startswith('/static-' + config.link)]
