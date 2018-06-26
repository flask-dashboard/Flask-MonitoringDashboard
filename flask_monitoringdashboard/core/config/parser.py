"""
    Helper functions for parsing the arguments from the config file
"""
import ast
import os

from flask_monitoringdashboard.core.logger import log


def parse_version(parser, header, version):
    """
    Parse the version given in the config-file.
    If both GIT and VERSION are used, the GIT argument is used.
    :param parser: the parser to be used for parsing
    :param header: name of the header in the configuration file
    :param version: the default version
    """
    version = parse_string(parser, header, 'APP_VERSION', version)
    if parser.has_option(header, 'GIT'):
        git = parser.get(header, 'GIT')
        try:
            # current hash can be found in the link in HEAD-file in git-folder
            # The file is specified by: 'ref: <location>'
            git_file = (open(os.path.join(git, 'HEAD')).read().rsplit(': ', 1)[1]).rstrip()
            # read the git-version
            version = open(git + '/' + git_file).read()
            # cut version to at most 6 chars
            return version[:6]
        except IOError:
            log("Error reading one of the files to retrieve the current git-version.")
            raise
    return version


def parse_string(parser, header, arg_name, arg_value):
    """
    Parse an argument from the given parser. If the argument is not specified, return the default value
    :param parser: the parser to be used for parsing
    :param header: name of the header in the configuration file
    :param arg_name: name in the configuration file
    :param arg_value: default value, the the value is not found
    """
    if parser.has_option(header, arg_name):
        return parser.get(header, arg_name)
    return arg_value


def parse_bool(parser, header, arg_name, arg_value):
    """
    Parse an argument from the given parser. If the argument is not specified, return the default value
    :param parser: the parser to be used for parsing
    :param header: name of the header in the configuration file
    :param arg_name: name in the configuration file
    :param arg_value: default value, the the value is not found
    """
    if parser.has_option(header, arg_name):
        return parser.get(header, arg_name) == 'True'
    return arg_value


def parse_literal(parser, header, arg_name, arg_value):
    """
    Parse an argument from the given parser. If the argument is not specified, return the default value
    :param parser: the parser to be used for parsing
    :param header: name of the header in the configuration file
    :param arg_name: name in the configuration file
    :param arg_value: default value, the the value is not found
    """
    if parser.has_option(header, arg_name):
        return ast.literal_eval(parser.get(header, arg_name))
    return arg_value
