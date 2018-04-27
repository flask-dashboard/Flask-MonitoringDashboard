import plotly
import plotly.graph_objs as go
from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.database.monitor_rules import get_monitor_names
from flask_monitoringdashboard.database.tests import get_res_current, get_measurements
from flask_monitoringdashboard.database.tests import get_tests, get_results, get_suites, get_test_measurements
from flask_monitoringdashboard.database.tests_grouped import get_tests_grouped
from flask_monitoringdashboard.core.auth import secure


@blueprint.route('/testmonitor/<test>')
@secure
def test_result(test):
    return render_template('testmonitor/testresult.html', link=config.link, session=session, name=test,
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

    return render_template('testmonitor/testmonitor.html', link=config.link, session=session, curr=3,
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
