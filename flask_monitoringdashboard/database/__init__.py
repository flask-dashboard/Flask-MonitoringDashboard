"""Creates the database.
For information about how to access the database via a session-variable, see: session_scope()
"""
from flask_monitoringdashboard import config

if config.database_name.startswith("mongodb"):
    from flask_monitoringdashboard.database.data_base_queries.mongo_db_objects import *
else:
    from flask_monitoringdashboard.database.data_base_queries.sql_objects import *
