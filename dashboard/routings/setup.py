from flask import session, request, render_template

from dashboard import blueprint, config, user_app
from dashboard.database.endpoint import get_monitor_rule, update_monitor_rule, get_last_accessed_times
from dashboard.database.monitor_rules import reset_monitor_endpoints
from dashboard.database.tests import get_tests, get_results, get_suites
from dashboard.database.tests import get_line_results, get_res_current, get_measurements
from dashboard.forms import MonitorDashboard
from dashboard.measurement import track_performance
from dashboard.security import secure

import pygal
import plotly
import plotly.graph_objs as go


@blueprint.route('/settings', methods=['GET', 'POST'])
@secure
def settings():
    password = 'x' * len(config.password)
    return render_template('settings.html', link=config.link, session=session, config=config, pw=password)


def formatter(x):
    sec = x // 1000
    ms = round(x % 1000, 2)
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}s and {1}ms'.format(sec, ms)


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

    return render_template('rules.html', link=config.link, curr=1, rules=all_rules, access=la, form=form,
                           session=session,
                           values=values)


@blueprint.route('/testmonitor')
@secure
def testmonitor():
    data = get_line_results()
    times_data = None
    if data:
        times_chart = pygal.HorizontalBar(height=100 + len(data) * 30)
        times_chart.x_labels = []
        list_avg = []
        list_min = []
        list_max = []
        list_count = []
        for d in data:
            times_chart.x_labels.append(d.version)
            list_min.append(d.min)
            list_avg.append(d.avg)
            list_max.append(d.max)
            list_count.append(d.count)
        times_chart.add('Minimum', list_min, formatter=formatter)
        times_chart.add('Average', list_avg, formatter=formatter)
        times_chart.add('Maximum', list_max, formatter=formatter)
        times_data = times_chart.render_data_uri()

    return render_template('testmonitor.html', link=config.link, session=session, curr=3,
                           tests=get_tests(), results=get_results(),
                           res_current_version=get_res_current(config.version), times_data=times_data,
                           boxplot=get_boxplot())


def get_boxplot():
    data = []
    suites = get_suites()
    for s in suites:
        values = [str(c.execution_time) for c in get_measurements(suite=s.suite)]

        data.append(go.Box(
            x=values,
            name="{0}".format(s.suite)))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(suites),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution times for every Travis build',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(
            title='Build',
            autorange='reversed'
        ),
        margin=go.Margin(
            l=200
        )
    )

    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
