from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import get_layout, get_figure, get_margin, heatmap
from flask_monitoringdashboard.database.function_calls import get_versions, \
    get_hits_per_version


@blueprint.route('/measurements/version_usage')
@secure
def version_usage():
    return render_template('dashboard/graph.html', graph=get_version_usage(), title='Version Usage')


def get_version_usage():
    """
    Used for getting a Heatmap with an overview of which endpoints are used in which versions
    :return:
    """
    all_endpoints = []
    versions = get_versions()

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
        total_hits = max(1, sum([record.count for record in hits_version[version]]))

        for record in hits_version[version]:
            data[record.endpoint][version] = record.count / total_hits

    for i in range(len(all_endpoints)):
        data_list.append([])
        for j in range(len(versions)):
            data_list[i].append(data[all_endpoints[i]][versions[j]])

    layout = get_layout(
        title='Heatmap of hits per endpoint per version',
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin()
    )

    trace = heatmap(
        z=data_list,
        x=versions,
        y=all_endpoints,
        colorscale=[[0, 'rgb(255, 255, 255)'], [0.01, 'rgb(240,240,240)'], [1, 'rgb(1, 1, 1)']],
        colorbar={
            'titleside': 'top',
            'tickmode': 'array',
            'tickvals': [1, 0],
            'ticktext': ['100%', '0%']
        }
    )
    return get_figure(layout=layout, data=[trace])
