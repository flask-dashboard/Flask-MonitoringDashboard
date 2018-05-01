import configparser
import unittest


class TestConfig(unittest.TestCase):

    def test_init_from(self):
        """
            Test whether the group_by returns the right result
        """
        import flask_monitoringdashboard as dashboard
        dashboard.config.init_from()
        dashboard.config.init_from(file='config.cfg')

    def test_parser(self):
        """
            Test whether the parser reads the right values
        """
        from flask_monitoringdashboard.core.config.parser import parse_literal, parse_bool, parse_string, parse_version, HEADER_NAME
        parser = configparser.RawConfigParser()
        version = '1.2.3'
        string = 'string-value'
        bool = 'False'
        literal = "['a', 'b', 'c']"
        literal2 = '1.23'

        parser.add_section(HEADER_NAME)
        parser.set(HEADER_NAME, 'APP_VERSION', version)
        parser.set(HEADER_NAME, 'string', string)
        parser.set(HEADER_NAME, 'bool', bool)
        parser.set(HEADER_NAME, 'literal', literal)
        parser.set(HEADER_NAME, 'literal2', literal2)

        self.assertEqual(parse_version(parser, 'default'), version)
        self.assertEqual(parse_string(parser, 'string', 'default'), string)
        self.assertEqual(parse_bool(parser, 'bool', 'True'), False)
        self.assertEqual(parse_literal(parser, 'literal', 'default'), ['a', 'b', 'c'])
        self.assertEqual(parse_literal(parser, 'literal2', 'default'), 1.23)
