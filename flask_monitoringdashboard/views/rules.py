from flask import session, request, render_template

from flask_monitoringdashboard import blueprint, config, user_app
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times
from flask_monitoringdashboard.database.monitor_rules import reset_monitor_endpoints
from flask_monitoringdashboard.forms import MonitorDashboard
from flask_monitoringdashboard.measurement import track_performance
from flask_monitoringdashboard.security import admin_secure


@blueprint.route('/rules', methods=['GET', 'POST'])
@admin_secure
def rules():
    form = MonitorDashboard()
    values = {}
    all_rules = user_app.url_map.iter_rules()

    if request.method == 'POST' and form.validate():
        # Remove the monitor endpoints from the database
        reset_monitor_endpoints()

        for rule in user_app.url_map.iter_rules():
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

    # store the result from the database in values (used for rendering)
    for rule in user_app.url_map.iter_rules():
        values[rule.endpoint] = get_monitor_rule(rule.endpoint).monitor

    la = get_last_accessed_times()

    # filter dashboard rules
    all_rules = [r for r in all_rules if not r.rule.startswith('/' + config.link)
                 and not r.rule.startswith('/static-' + config.link)]
    colors = {}
    for rule in all_rules:
        colors[rule.endpoint] = get_color(rule.endpoint)

    return render_template('rules.html', link=config.link, curr=1, rules=all_rules, access=la, form=form,
                           session=session, values=values, colors=colors)
