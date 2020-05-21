import configparser
import os

from flask_monitoringdashboard.core.config.parser import (
    get_environment_var,
    parse_literal,
    parse_bool,
    parse_string,
    parse_version,
)


def test_init_from(config):
    """Test whether the group_by returns the right result."""

    config.init_from()
    config.init_from(file='../../config.cfg')


def test_parser():
    """Test whether the parser reads the right values."""

    parser = configparser.RawConfigParser()
    version = '1.2.3'
    string = 'string-value'
    bool = 'False'
    literal = "['a', 'b', 'c']"
    literal2 = '1.23'
    section = 'dashboard'

    parser.add_section(section)
    parser.set(section, 'APP_VERSION', version)
    parser.set(section, 'string', string)
    parser.set(section, 'bool', bool)
    parser.set(section, 'literal', literal)
    parser.set(section, 'literal2', literal2)

    assert parse_version(parser, section, 'default') == version
    assert parse_string(parser, section, 'string', 'default') == string
    assert not parse_bool(parser, section, 'bool', 'True')
    assert parse_literal(parser, section, 'literal', 'default') == ['a', 'b', 'c']
    assert parse_literal(parser, section, 'literal2', 'default') == 1.23

