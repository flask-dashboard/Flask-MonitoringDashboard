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

from . import heatmap
from . import outliers
from . import time_user
from . import time_version
from . import version_ip
from . import version_user

