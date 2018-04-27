"""
    Contains all endpoints that can be found in the Dashboard-menu on the left.
    The endpoints are the following:
    - Overview: shows a quick overview of every endpoint.
    - Heatmap: shows a heatmap of the number of requests.
    - Version usage: shows how much a certain version is used.
    - Requests per endpoint: shows how much requests a certain endpoint received.
    - Time per version: Shows the overall execution time for all versions.
    - Time per endpoint: Shows the overall execution time for all endpoints.
"""

from flask_monitoringdashboard.views.dashboard.endpoints import page_boxplot_per_endpoint
from flask_monitoringdashboard.views.dashboard.heatmap import heatmap
from flask_monitoringdashboard.views.dashboard.overview import overview
from flask_monitoringdashboard.views.dashboard.requests import page_number_of_requests_per_endpoint
from flask_monitoringdashboard.views.dashboard.version_usage import version_usage
from flask_monitoringdashboard.views.dashboard.versions import page_boxplot_per_version
