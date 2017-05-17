from flask import session, request

from dashboard import user_app, link, version, env, user_var, database_name
from dashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times
from dashboard.database.monitor_rules import reset_monitor_endpoints
from dashboard.database.settings import get_setting, set_setting
from dashboard.forms import MonitorDashboard, ChangeSetting
from dashboard.measurement import track_performance
from dashboard.security import secure


@user_app.route('/' + link + '/settings', methods=['GET', 'POST'])
@secure
def dashboard_settings():
    form = ChangeSetting()
    form.username.data = get_setting('username', 'admin')
    old_password = get_setting('password', 'admin')
    old_password = 'x' * len(old_password)

    if request.method == 'POST' and form.validate():
        set_setting('username', form.username.data)
        if form.password.data:
            set_setting('password', form.password.data)

    return env.get_template('settings.html').\
        render(link=link, session=session, version=version, database_name=database_name, user_var=user_var,
               form=form, old_password=old_password)


@user_app.route('/' + link + '/rules', methods=['GET', 'POST'])
@secure
def render_dashboard():
    form = MonitorDashboard()
    values = {}
    rules = user_app.url_map.iter_rules()

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
                user_app.view_functions[rule.endpoint] = track_performance(user_app.view_functions[rule.endpoint])

    # store the result from the database in values (used for rendering)
    for rule in user_app.url_map.iter_rules():
        values[rule.endpoint] = get_monitor_rule(rule.endpoint).monitor

    la = get_last_accessed_times()

    return env.get_template('rules.html').\
        render(rules=rules, access=la, form=form, link=link, session=session, values=values)
