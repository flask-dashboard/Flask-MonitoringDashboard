"""
    Helper functions for parsing the arguments from the config file
"""
import ast
import os

HEADER_NAME = 'dashboard'


def parse_version(parser, version):
    """
    Parse the version given in the config-file.
    If both GIT and VERSION are used, the GIT argument is used.
    :param parser: the parser to be used for parsing
    :param version: the default version
    """
    version = parse_string(parser, 'APP_VERSION', version)
    if parser.has_option(HEADER_NAME, 'GIT'):
        git = parser.get(HEADER_NAME, 'GIT')
        try:
            # current hash can be found in the link in HEAD-file in git-folder
            # The file is specified by: 'ref: <location>'
            git_file = (open(os.path.join(git, 'HEAD')).read().rsplit(': ', 1)[1]).rstrip()
            # read the git-version
            version = open(git + '/' + git_file).read()
            # cut version to at most 6 chars
            return version[:6]
        except IOError:
            print("Error reading one of the files to retrieve the current git-version.")
            raise
    return version


def parse_string(parser, arg_name, arg_value):
    """
    Parse an argument from the given parser. If the argument is not specified, return the default value
    :return:
    """
    if parser.has_option(HEADER_NAME, arg_name):
        return parser.get(HEADER_NAME, arg_name)
    return arg_value


def parse_bool(parser, arg_name, arg_value):
    """
    Parse an argument from the given parser. If the argument is not specified, return the default value
    :return:
    """
    if parser.has_option(HEADER_NAME, arg_name):
        return parser.get(HEADER_NAME, arg_name) == 'True'
    return arg_value


def parse_literal(parser, arg_name, arg_value):
    """
    Parse an argument from the given parser. If the argument is not specified, return the default value
    :return:
    """
    if parser.has_option(HEADER_NAME, arg_name):
        return ast.literal_eval(parser.get(HEADER_NAME, arg_name))
    return arg_value
