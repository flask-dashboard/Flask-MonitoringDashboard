import plotly
import plotly.graph_objs as go
from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.colors import get_color
from flask_monitoringdashboard.database.function_calls import get_times, get_versions, \
    get_data_per_version
from flask_monitoringdashboard.security import secure


@blueprint.route('/measurements/versions')
@secure
def page_boxplot_per_version():
    colors = {}
    for result in get_times():
        colors[result.endpoint] = get_color(result.endpoint)
    return render_template('dashboard/dashboard.html', link=config.link, curr=2, session=session, index=4,
                           graph=get_boxplot_per_version())


def get_boxplot_per_version():
    """
    Creates a graph with the execution times per version
    :return:
    """
    versions = get_versions()

    if len(versions) == 0:
        return None

    data = []
    for v in versions:
        values = [c.execution_time for c in get_data_per_version(v.version)]
        data.append(go.Box(
            x=values,
            marker=dict(
                color=get_color(v.version)
            ),
            name="{0} {1}".format(v.version, v.startedUsingOn.strftime("%b %d %H:%M"))))

    layout = go.Layout(
        autosize=True,
        height=350 + 40 * len(versions),
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Execution time for every version',
        xaxis=dict(title='Execution time (ms)'),
        yaxis=dict(autorange='reversed'),
        margin=go.Margin(
            l=200
        )
    )
    return plotly.offline.plot(go.Figure(data=data, layout=layout), output_type='div', show_link=False)
