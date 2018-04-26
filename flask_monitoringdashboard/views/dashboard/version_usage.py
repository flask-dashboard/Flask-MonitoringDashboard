from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.plot import get_layout, get_figure, get_margin, heatmap
from flask_monitoringdashboard.database import FunctionCall
from flask_monitoringdashboard.database.count import count_requests
from flask_monitoringdashboard.database.function_calls import get_endpoints
from flask_monitoringdashboard.database.versions import get_versions

TITLE = 'Heatmap of the distribution of the hits per endpoint per version'


@blueprint.route('/measurements/version_usage')
@secure
def version_usage():
    return render_template('dashboard/graph.html', graph=get_version_usage(), title=TITLE)


def get_version_usage():
    """
    Used for getting a Heatmap with an overview of which endpoints are used in which versions
    :return:
    """
    endpoints = get_endpoints()
    versions = get_versions()

    hits = [[count_requests(e, FunctionCall.version == v) for v in versions] for e in endpoints]

    for i in range(len(versions)):  # compute the total number of hits in a specific version
        total_hits = max(1, sum([column[i] for column in hits]))

        for j in range(len(endpoints)):  # compute distribution
            hits[j][i] = hits[j][i] * 100 / total_hits

    layout = get_layout(
        title=TITLE,
        xaxis={'title': 'Versions', 'type': 'category'},
        yaxis={'type': 'category', 'autorange': 'reversed'},
        margin=get_margin()
    )

    trace = heatmap(
        z=hits,
        x=versions,
        y=endpoints,
        colorscale=[[0, 'rgb(255, 255, 255)'], [0.01, 'rgb(240,240,240)'], [1, 'rgb(1, 1, 1)']],
        colorbar={
            'titleside': 'top',
            'tickmode': 'array',
            'tickvals': [100, 0],
            'ticktext': ['100%', '0%']
        }
    )
    return get_figure(layout=layout, data=[trace])
