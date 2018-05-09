"""
    Contains all endpoints that present information about specific endpoints.
    The endpoints are the following:
    - heatmap/<end>: shows a heatmap of the usage for <end>
    - Time per version per user/<end>: shows an overview of the time per user per version for a given <end>
    - Time per version per ip/<end>: shows an overview of the time per user per ip for a given <end>
    - Time per version/<end>: shows an overview of all requests per version for a given <end>
    - Time per user/<end>: shows an overview of all requests per user for a given <end>
    - Outliers/<end>: shows information about requests that take too long.
"""

from flask_monitoringdashboard.views.details.heatmap import endpoint_hourly_load
from flask_monitoringdashboard.views.details.outliers import outliers
from flask_monitoringdashboard.views.details.time_user import users
from flask_monitoringdashboard.views.details.time_version import versions
from flask_monitoringdashboard.views.details.version_ip import version_ip
from flask_monitoringdashboard.views.details.version_user import version_user
