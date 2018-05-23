from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.forms import get_slider_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, boxplot
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.database import session_scope, TestRun
from flask_monitoringdashboard.database.count import count_builds
from flask_monitoringdashboard.database.count_group import get_value, count_times_tested, get_latest_test_version
from flask_monitoringdashboard.database.tests import get_test_suites, \
    get_test_measurements, get_suite_measurements, get_last_tested_times
from flask_monitoringdashboard.database.tests_grouped import get_tests_grouped, get_endpoint_names

AXES_INFO = '''The X-axis presents the execution time in ms. The Y-axis presents the
Travis builds of the Flask application.'''

CONTENT_INFO = '''In this graph, it is easy to compare the execution time of the different builds
to one another. This information may be useful to validate which endpoints need to be improved.'''


@blueprint.route('/test_build_performance', methods=['GET', 'POST'])
@secure
def test_build_performance():
    """
    Shows the performance results for all of the versions.
    :return:
    """
    with session_scope() as db_session:
        form = get_slider_form(count_builds(db_session), title='Select the number of builds')
    graph = get_boxplot(form=form)
    return render_template('fmd_dashboard/graph.html', graph=graph, title='Per-Build Performance',
                           information=get_information(AXES_INFO, CONTENT_INFO), form=form)


@blueprint.route('/testmonitor/<end>', methods=['GET', 'POST'])
@secure
def endpoint_test_details(end):
    """
    Shows the performance results for one specific unit test.
    :param end: the name of the unit test for which the results should be shown
    :return:
    """
    with session_scope() as db_session:
        form = get_slider_form(count_builds(db_session), title='Select the number of builds')
    graph = get_boxplot(endpoint=end, form=form)
    return render_template('fmd_testmonitor/endpoint.html', graph=graph, title='Per-Version Performance for ' + end,
                           information=get_information(AXES_INFO, CONTENT_INFO), endp=end, form=form)


@blueprint.route('/testmonitor')
@secure
def testmonitor():
    """
    Gives an overview of the unit test performance results and the endpoints that they hit.
    :return:
    """
    with session_scope() as db_session:
        endpoint_test_combinations = get_tests_grouped(db_session)

        tests_latest = count_times_tested(db_session, TestRun.version == get_latest_test_version(db_session))
        tests = count_times_tested(db_session)
        # Medians can only be calculated when the new way of data collection is implemented.
        # median_latest = get_endpoint_data_grouped(db_session, median, FunctionCall.time > week_ago)
        # median = get_test_data_grouped(db_session, median)
        tested_times = get_last_tested_times(db_session, endpoint_test_combinations)

        result = []
        for endpoint in get_endpoint_names(db_session):
            result.append({
                'name': endpoint,
                'color': get_color(endpoint),
                'tests-latest-version': get_value(tests_latest, endpoint),
                'tests-overall': get_value(tests, endpoint),
                # Medians can only be calculated when the new way of data collection is implemented.
                # 'median-latest-version': get_value(median_latest, endpoint),
                # 'median-overall': get_value(median, endpoint),
                'median-latest-version': -1,
                'median-overall': -1,
                'last-tested': get_value(tested_times, endpoint, default=None)
            })

        return render_template('fmd_testmonitor/testmonitor.html', result=result)


def get_boxplot(endpoint=None, form=None):
    """
    Generates a box plot visualization for the unit test performance results.
    :param endpoint: if specified, generate box plot for a specific test, otherwise, generate for all tests
    :param form: the form that can be used for showing a subset of the data
    :return:
    """
    trace = []
    with session_scope() as db_session:
        if form:
            suites = get_test_suites(db_session, limit=form.get_slider_value())
        else:
            suites = get_test_suites(db_session)

        if not suites:
            return None
        for s in suites:
            if endpoint:
                values = get_test_measurements(db_session, name=endpoint, suite=s.suite)
            else:
                values = get_suite_measurements(db_session, suite=s.suite)

            trace.append(boxplot(values=values, label='{} -'.format(s.suite)))

        layout = get_layout(
            xaxis={'title': 'Execution time (ms)'},
            yaxis={'title': 'Travis Build', 'autorange': 'reversed'}
        )

        return get_figure(layout=layout, data=trace)
