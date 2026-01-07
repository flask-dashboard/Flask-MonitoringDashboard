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


def test_data_retention_days_default(config):
    """Test that data_retention_days has correct default value."""
    from flask_monitoringdashboard.core.config import Config
    fresh_config = Config()
    assert fresh_config.data_retention_days == 30


def test_data_retention_days_parser():
    """Test that DATA_RETENTION_DAYS is correctly parsed from config."""
    parser = configparser.RawConfigParser()
    parser.add_section('database')
    parser.set('database', 'DATA_RETENTION_DAYS', '60')

    result = parse_literal(parser, 'database', 'DATA_RETENTION_DAYS', 30)
    assert result == 60


def test_data_retention_days_disable():
    """Test that DATA_RETENTION_DAYS can be set to 0 to disable cleanup."""
    parser = configparser.RawConfigParser()
    parser.add_section('database')
    parser.set('database', 'DATA_RETENTION_DAYS', '0')

    result = parse_literal(parser, 'database', 'DATA_RETENTION_DAYS', 30)
    assert result == 0

