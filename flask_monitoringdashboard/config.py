import configparser
import os
import ast


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

        # define a custom function to retrieve the session_id or username
        self.get_group_by = None

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

            :param file: a string pointing to the location of the config-file
            :param envvar: a string specifying which environment variable holds the config file location
        """

        if envvar:
            file = os.getenv(envvar)
        if not file:
            print("No configuration file specified. Please do so.")

        # When collecting unit test performance results, create log file
        log_dir = os.getenv('DASHBOARD_LOG_DIR')
        if log_dir:
            log = open(log_dir + "endpoint_hits.log", "w")
            log.write("\"time\",\"endpoint\"\n")
            log.close()

        parser = configparser.RawConfigParser()
        try:
            parser.read(file)
            if parser.has_option('dashboard', 'APP_VERSION'):
                self.version = parser.get('dashboard', 'APP_VERSION')
            if parser.has_option('dashboard', 'CUSTOM_LINK'):
                self.link = parser.get('dashboard', 'CUSTOM_LINK')
            if parser.has_option('dashboard', 'DATABASE'):
                self.database_name = parser.get('dashboard', 'DATABASE')
            if parser.has_option('dashboard', 'TEST_DIR'):
                self.test_dir = parser.get('dashboard', 'TEST_DIR')

            # For manually defining colors of specific endpoints
            if parser.has_option('dashboard', 'COLORS'):
                self.colors = ast.literal_eval(parser.get('dashboard', 'COLORS'))

            # When the option git is selected, it overrides the given version
            if parser.has_option('dashboard', 'GIT'):
                git = parser.get('dashboard', 'GIT')
                try:
                    # current hash can be found in the link in HEAD-file in git-folder
                    # The file is specified by: 'ref: <location>'
                    git_file = (open(os.path.join(git, 'HEAD')).read().rsplit(': ', 1)[1]).rstrip()
                    # read the git-version
                    self.version = open(git + '/' + git_file).read()
                    # cut version to at most 6 chars
                    self.version = self.version[:6]
                except IOError:
                    print("Error reading one of the files to retrieve the current git-version.")
                    raise

            # provide username and/or password ..
            # .. for admin
            if parser.has_option('dashboard', 'USERNAME'):
                self.username = parser.get('dashboard', 'USERNAME')
            if parser.has_option('dashboard', 'PASSWORD'):
                self.password = parser.get('dashboard', 'PASSWORD')
            # .. for guest (a guest can only see the results, but cannot configure or download any data)
            if parser.has_option('dashboard', 'GUEST_USERNAME'):
                self.guest_username = parser.get('dashboard', 'GUEST_USERNAME')
            if parser.has_option('dashboard', 'GUEST_PASSWORD'):
                self.guest_password = ast.literal_eval(parser.get('dashboard', 'GUEST_PASSWORD'))

            # when an outlier detection constant has been set up:
            if parser.has_option('dashboard', 'OUTLIER_DETECTION_CONSTANT'):
                self.outlier_detection_constant = ast.literal_eval(
                    parser.get('dashboard', 'OUTLIER_DETECTION_CONSTANT'))

            # when a security token is provided:
            if parser.has_option('dashboard', 'security_token'):
                self.security_token = parser.get('dashboard', 'SECURITY_TOKEN')

        except configparser.Error:
            raise
