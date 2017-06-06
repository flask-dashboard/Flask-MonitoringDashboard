from flask import session, request, render_template

from dashboard import blueprint, config, user_app
from dashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times
from dashboard.database.monitor_rules import reset_monitor_endpoints
from dashboard.database.tests import get_tests, reset_run, update_test, get_test
from dashboard.database.settings import get_setting, set_setting
from dashboard.forms import MonitorDashboard, ChangeSetting, RunTests
from dashboard.measurement import track_performance
from dashboard.security import secure
from unittest import TestLoader

import datetime


@blueprint.route('/settings', methods=['GET', 'POST'])
@secure
def settings():
    form = ChangeSetting()
    form.username.data = get_setting('username', 'admin')
    old_password = get_setting('password', 'admin')
    old_password = 'x' * len(old_password)

    if request.method == 'POST' and form.validate():
        set_setting('username', form.username.data)
        if form.password.data:
            set_setting('password', form.password.data)

    return render_template('settings.html', session=session, version=config.version,
                           database_name=config.database_name, group=config.get_group_by(), form=form,
                           testDir=config.test_dir, old_password=old_password)


@blueprint.route('/rules', methods=['GET', 'POST'])
@secure
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

    return render_template('rules.html', rules=all_rules, access=la, form=form, session=session, values=values)


@blueprint.route('/testmonitor', methods=['GET', 'POST'])
@secure
def testmonitor():
    form = RunTests()
    if request.method == 'POST' and form.validate():

        suites = TestLoader().discover(config.test_dir, pattern="*test*.py")
        for suite in suites:
            for case in suite:
                for test in case:
                    result = None
                    result = test.run(result)
                    print(result)

        reset_run()
        for data in request.form:
            if data.startswith('checkbox-'):
                name = data.rsplit('-', 1)[1]
                update_test(name, True, get_test(name).timesRun + 1, datetime.datetime.now())

    return render_template('testmonitor.html', session=session, form=form, tests=get_tests())
