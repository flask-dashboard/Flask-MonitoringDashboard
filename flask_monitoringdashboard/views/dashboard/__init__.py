"""
    Contains all menu items that can be found in the Dashboard-menu on the left.
    The endpoints are the following:
    - Overview: shows a quick overview of every endpoint.
    - Hourly API Utilization: shows a heatmap of the number of requests.
    - Multi Version API Utilization: shows how much a certain version is used.
    - Daily API Utilization: shows how many requests are received per day.
    - API Performance: Shows performance box plots for every endpoint.
"""

from flask_monitoringdashboard.views.dashboard.endpoints import endpoints
from flask_monitoringdashboard.views.dashboard.heatmap import hourly_load
from flask_monitoringdashboard.views.dashboard.overview import overview
from flask_monitoringdashboard.views.dashboard.requests import requests
from flask_monitoringdashboard.views.dashboard.version_usage import version_usage
