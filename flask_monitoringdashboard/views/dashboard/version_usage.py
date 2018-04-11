import plotly
import plotly.graph_objs as go
from flask import session, render_template

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.database.function_calls import get_versions, \
    get_hits_per_version
from flask_monitoringdashboard.security import secure


@blueprint.route('/measurements/version_usage')
@secure
def version_usage():
    return render_template('dashboard/dashboard.html', link=config.link, curr=2, session=session, index=2,
                           graph=get_version_usage())


def get_version_usage():
    """
    Used for getting a Heatmap with an overview of which endpoints are used in which versions
    :return:
    """
    all_endpoints = []
    versions = [v.version for v in get_versions()]

    hits_version = {}
    for version in versions:
        hits_version[version] = get_hits_per_version(version)
        for record in hits_version[version]:
            if record.endpoint not in all_endpoints:
                all_endpoints.append(record.endpoint)

    all_endpoints = sorted(all_endpoints)
    data = {}
    data_list = []
    for endpoint in all_endpoints:
        data[endpoint] = {}
        for version in versions:
            data[endpoint][version] = 0

    for version in versions:
        total_hits = sum([record.count for record in hits_version[version]])
        if total_hits == 0:
            total_hits = 1  # avoid division by zero

        for record in hits_version[version]:
            data[record.endpoint][version] = record.count / total_hits

    for i in range(len(all_endpoints)):
        data_list.append([])
        for j in range(len(versions)):
            data_list[i].append(data[all_endpoints[i]][versions[j]])

    layout = go.Layout(
        autosize=True,
        height=800,
        plot_bgcolor='rgba(249,249,249,1)',
        showlegend=False,
        title='Heatmap of hits per endpoint per version',
        xaxis=go.XAxis(title='Versions', type='category'),
        yaxis=dict(type='category', autorange='reversed'),
        margin=go.Margin(
            l=200
        )
    )

    trace = go.Heatmap(
        z=data_list,
        x=versions,
        y=all_endpoints,
        colorscale=[[0, 'rgb(255, 255, 255)'], [0.01, 'rgb(240,240,240)'],[1, 'rgb(1, 1, 1)']],
        colorbar=dict(
            titleside='top',
            tickmode='array',
            tickvals=[1, 0],
            ticktext=['100%', '0%'],
            # ticks='outside'
        )
    )
    return plotly.offline.plot(go.Figure(data=[trace], layout=layout), output_type='div', show_link=False)
