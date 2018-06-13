import unittest


class TestColors(unittest.TestCase):

    def test_get_color(self):
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.core.colors import get_color

        config.colors['endpoint'] = '[0, 1, 2]'

        self.assertEqual(get_color('endpoint'), 'rgb(0, 1, 2)')
        self.assertIn(get_color('main'), ['rgb(140, 191, 64)', 'rgb(140.0, 191.0, 64.0)'])
