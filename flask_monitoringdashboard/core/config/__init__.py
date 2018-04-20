import configparser
import os

from flask_monitoringdashboard.core.config.parser import parse_string, parse_version, parse_bool, parse_literal


class Config(object):
    """
        The settings can be changed by setting up a config file. For an example of a config file, see
         config.cfg in the main-directory. 
    """

    def __init__(self):
        """
            Sets the default values for the project
        """
        self.version = '1.0'
        self.link = 'dashboard'
        self.database_name = 'sqlite:///flask_monitoringdashboard.db'
        self.test_dir = None
        self.username = 'admin'
        self.password = 'admin'
        self.guest_username = 'guest'
        self.guest_password = ['guest_password']
        self.outlier_detection_constant = 2.5
        self.colors = {}
        self.security_token = 'cc83733cb0af8b884ff6577086b87909'
        self.outliers_enabled = True

        # define a custom function to retrieve the session_id or username
        self.group_by = None

    def init_from(self, file=None, envvar=None):
        """
            The config_file must at least contains the following variables in section 'dashboard':
            APP_VERSION: the version of the app that you use. Updating the version helps in 
                showing differences in execution times of a function over a period of time.
            CUSTOM_LINK: The dashboard can be visited at localhost:5000/{{CUSTOM_LINK}}.
            DATABASE: Suppose you have multiple projects where you're working on and want to 
                separate the results. Then you can specify different database_names, such that the 
                result of each project is stored in its own database.
            
            Since updating the version in the config-file when updating code isn't very useful, it
            is a better idea to provide the location of the git-folder. From the git-folder. The 
            version automatically retrieved by reading the commit-id (hashed value):
            GIT = If you're using git, then it is easier to set the location to the .git-folder, 
                The location is relative to the config-file.

            USERNAME: for logging into the dashboard, a username and password is required. The
                username can be set using this variable.
            PASSWORD: same as for the username, but this is the password variable.
            GUEST_USERNAME: A guest can only see the results, but cannot configure/download data.
            GUEST_PASSWORD: A guest can only see the results, but cannot configure/download data.

            OUTLIER_DETECTION_CONSTANT: When the execution time is more than this constant *
                average, extra information is logged into the database. A default value for this
                variable is 2.5, but can be changed in the config-file.

            SECURITY_TOKEN: Used for getting the data in /get_json_data/<security_token>

            OUTLIERS_ENABLED: Whether you want the Dashboard to collect extra information about outliers.

            :param file: a string pointing to the location of the config-file
            :param envvar: a string specifying which environment variable holds the config file location
        """

        if envvar:
            file = os.getenv(envvar)
        if not file:
            print("No configuration file specified. Please do so.")
            return

        create_log_file()

        parser = configparser.RawConfigParser()
        try:
            parser.read(file)
            parse_version(parser, self.version)

            self.link = parse_string(parser, 'CUSTOM_LINK', self.link)
            self.database_name = parse_string(parser, 'DATABASE', self.database_name)
            self.test_dir = parse_string(parser, 'TEST_DIR', self.test_dir)
            self.security_token = parse_string(parser, 'SECURITY_TOKEN', self.security_token)
            self.outliers_enabled = parse_bool(parser, 'OUTLIERS_ENABLED', self.outliers_enabled)
            self.colors = parse_literal(parser, 'COLORS', self.colors)
            self.outlier_detection_constant = parse_literal(parser, 'OUTlIER_DETECTION_CONSTANT',
                                                            self.outlier_detection_constant)
            self.username = parse_string(parser, 'USERNAME', self.username)
            self.password = parse_string(parser, 'PASSWORD', self.password)
            self.guest_username = parse_string(parser, 'GUEST_USERNAME', self.guest_username)
            self.guest_password = parse_literal(parser, 'GUEST_PASSWORD', self.guest_password)
        except configparser.Error:
            raise


def create_log_file():
    """
    Create a file and put some content in it. Used for unit test performance results.
    """
    log_dir = os.getenv('DASHBOARD_LOG_DIR')
    if log_dir:
        log = open(log_dir + "endpoint_hits.log", "w")
        log.write("\"time\",\"endpoint\"\n")
        log.close()
