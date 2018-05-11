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

from flask_monitoringdashboard.views.dashboard.endpoints import endpoints
from flask_monitoringdashboard.views.dashboard.heatmap import hourly_load
from flask_monitoringdashboard.views.dashboard.overview import overview
from flask_monitoringdashboard.views.dashboard.requests import requests
from flask_monitoringdashboard.views.dashboard.version_usage import version_usage
