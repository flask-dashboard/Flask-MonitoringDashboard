from flask import session, request, render_template

from flask_monitoringdashboard import blueprint, config, user_app
from flask_monitoringdashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times
from flask_monitoringdashboard.database.monitor_rules import reset_monitor_endpoints, get_monitor_names
from flask_monitoringdashboard.database.tests import get_tests, get_results, get_suites, get_test_measurements
from flask_monitoringdashboard.database.tests import get_res_current, get_measurements
from flask_monitoringdashboard.database.tests_grouped import get_tests_grouped
from flask_monitoringdashboard.forms import MonitorDashboard
from flask_monitoringdashboard.measurement import track_performance
from flask_monitoringdashboard.security import secure, admin_secure
from flask_monitoringdashboard.colors import get_color

import plotly
import plotly.graph_objs as go


@blueprint.route('/settings', methods=['GET', 'POST'])
@admin_secure
def settings():
    password = 'x' * len(config.password)
    return render_template('dashboard/settings.html', link=config.link, session=session, config=config, pw=password)


def formatter(x):
    sec = x // 1000
    ms = round(x % 1000, 2)
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}s and {1}ms'.format(sec, ms)


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

    # filter flask_monitoringdashboard rules
    all_rules = [r for r in all_rules if not r.rule.startswith('/' + config.link)
                 and not r.rule.startswith('/static-' + config.link)]
    colors = {}
    for rule in all_rules:
        colors[rule.endpoint] = get_color(rule.endpoint)

    return render_template('dashboard/rules.html', link=config.link, curr=1, rules=all_rules, access=la, form=form,
                           session=session, values=values, colors=colors)


@blueprint.route('/testmonitor/<test>')
@secure
def test_result(test):
    return render_template('dashboard/testresult.html', link=config.link, session=session, name=test,
                           boxplot=get_boxplot(test))


@blueprint.route('/testmonitor')
@secure
def testmonitor():
    endp_names = []
    for name in get_monitor_names():
        endp_names.append(name.endpoint)
    tests = get_tests_grouped()
    grouped = {}
    cols = {}
    for t in tests:
        if t.endpoint not in grouped:
            grouped[t.endpoint] = []
            cols[t.endpoint] = get_color(t.endpoint)
        if t.test_name not in grouped[t.endpoint]:
            grouped[t.endpoint].append(t.test_name)

    return render_template('dashboard/testmonitor.html', link=config.link, session=session, curr=3,
                           tests=get_tests(), endpoints=endp_names, results=get_results(), groups=grouped,
                           colors=cols, res_current_version=get_res_current(config.version), boxplot=get_boxplot(None))


def get_boxplot(test):
    data = []
    suites = get_suites()
    if not suites:
        return None
    for s in suites:
        if test:
            values = [str(c.execution_time) for c in get_test_measurements(name=test, suite=s.suite)]
        else:
            values = [str(c.execution_time) for c in get_measurements(suite=s.suite)]

        data.append(go.Box(
            x=values,
            name="{0} ({1})".format(s.suite, len(values))))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(suites),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution times for every Travis build',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(
            title='Build (measurements)',
            autorange='reversed'
        )
    )

    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
