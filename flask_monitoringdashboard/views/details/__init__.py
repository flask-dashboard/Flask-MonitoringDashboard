"""
    Contains all views that present information about specific endpoints.
    The endpoints are the following:
    - heatmap/<endpoint_id>: shows a heatmap of the usage for <endpoint_id>
    - Time per version per user/<endpoint_id>: shows an overview of the time per user per version for a given
            <endpoint_id>
    - Time per version per ip/<endpoint_id>: shows an overview of the time per user per ip for a given <endpoint_id>
    - Time per version/<endpoint_id>: shows an overview of all requests per version for a given <endpoint_id>
    - Time per user/<endpoint_id>: shows an overview of all requests per user for a given <endpoint_id>
    - Outliers/<endpoint_id>: shows information about requests that take too long.
"""

from flask_monitoringdashboard.views.details.heatmap import endpoint_hourly_load
from flask_monitoringdashboard.views.details.outliers import outliers
from flask_monitoringdashboard.views.details.time_user import users
from flask_monitoringdashboard.views.details.time_version import versions
from flask_monitoringdashboard.views.details.version_ip import version_ip
from flask_monitoringdashboard.views.details.version_user import version_user
from flask_monitoringdashboard.views.details.profiler import profiler
from flask_monitoringdashboard.views.details.grouped_profiler import grouped_profiler
