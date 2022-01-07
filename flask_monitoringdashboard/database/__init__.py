"""Creates the database.
For information, following the lines to access the database via the DatabaseConnectionWrapper:
database_connection_wrapper = DatabaseConnectionWrapper()
with database_connection_wrapper.database_connection.session_scope() as session:
    database_connection_wrapper.database_connection.<OPERATION>()
"""
from flask_monitoringdashboard.database.data_base_queries.mongo_db_objects import mongodb_database_connection
from flask_monitoringdashboard.database.data_base_queries.sql_objects import sql_database_connection
current_config = None


class DatabaseConnectionWrapper:
    def __init__(self, config=None):
        global current_config
        if config:
            current_config = config
        if not current_config:
            raise ValueError("MISSING CONFIG")
        self.database_name = current_config.database_name
        if current_config.database_name.startswith("mongodb"):
            self.__database_connection = mongodb_database_connection
        else:
            self.__database_connection = sql_database_connection

    @property
    def database_connection(self):
        return self.__database_connection

    def get_database_type(self):
        return type(self.__database_connection).__name__

    def apply_config(self, new_config):
        """
        This method applies now configuration. If the database_name changes,
        then it return a new instance of the wrapper pointing to the new config
        """
        new_database_connection_wrapper = DatabaseConnectionWrapper(config=new_config)
        if self.get_database_type() != new_database_connection_wrapper.get_database_type() and \
                self.database_name != new_database_connection_wrapper.database_name:
            new_database_connection_wrapper.database_connection.connect()
            new_database_connection_wrapper.database_connection.init_database()
            return new_database_connection_wrapper
        return self
