import plotly
import plotly.graph_objs as go
from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.tests import get_res_current, get_measurements
from flask_monitoringdashboard.database.tests import get_tests, get_results, get_suites, get_test_measurements
from flask_monitoringdashboard.database.tests_grouped import get_tests_grouped


@blueprint.route('/testmonitor/<test>')
@secure
def test_result(test):
    """
    Shows the performance results for one specific unit test.
    :param test: the name of the unit test for which the results should be shown
    :return:
    """
    return render_template('fmd_testmonitor/testresult.html', link=config.link, session=session, name=test,
                           boxplot=get_boxplot(test))


@blueprint.route('/testmonitor')
@secure
def testmonitor():
    """
    Gives an overview of the unit test performance results and the endpoints that they hit.
    :return:
    """
    with session_scope() as db_session:
        endpoint_test_combinations = get_tests_grouped(db_session)
        tests_grouped_by_endpoint = {}
        endpoint_colors = {}
        for combination in endpoint_test_combinations:
            if combination.endpoint not in tests_grouped_by_endpoint:
                tests_grouped_by_endpoint[combination.endpoint] = []
                endpoint_colors[combination.endpoint] = get_color(combination.endpoint)
            tests_grouped_by_endpoint[combination.endpoint].append(combination.test_name)

        return render_template('fmd_testmonitor/testmonitor.html', tests=get_tests(db_session),
                               results=get_results(db_session), groups=tests_grouped_by_endpoint,
                               colors=endpoint_colors,
                               res_current_version=get_res_current(db_session, config.version), boxplot=get_boxplot())


def get_boxplot(test=None):
    """
    Generates a box plot visualization for the unit test performance results.
    :param test: if specified, generate box plot for a specific test, otherwise, generate for all tests
    :return:
    """
    data = []
    with session_scope() as db_session:
        suites = get_suites(db_session)
    if not suites:
        return None
    for s in suites:
        if test:
            values = [str(c.execution_time) for c in get_test_measurements(db_session, name=test, suite=s.suite)]
        else:
            values = [str(c.execution_time) for c in get_measurements(db_session, suite=s.suite)]

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
