"""
    This file contains all unit tests for the host-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/host.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_hosts
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME, IP


class TestHost(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_host(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.database.host import add_host
        name2 = 'main2'
        self.assertNotEqual(NAME, name2, 'Both cannot be equal, otherwise the test will fail')
        with session_scope() as db_session:
            number_of_hosts = count_hosts(db_session)
            add_host(db_session, config.host_name, IP)
            self.assertEqual(count_hosts(db_session), number_of_hosts + 1)

    def test_hosts(self):
        """
            Test retrieval of all hosts
        """

        from flask_monitoringdashboard.database.host import get_hosts
        with session_scope() as db_session:
            number_of_hosts = count_hosts(db_session)
            self.assertEqual(len(list(get_hosts(db_session))), number_of_hosts)

    def test_get_host_name_by_id(self):
        """
        Tests retrieval of host by name
        """

        from flask_monitoringdashboard.database.host import get_host_name_by_id
        with session_scope() as db_session:
            host = get_host_name_by_id(db_session, 1)
            self.assertEqual(host.id, 1)

    def test_get_host_hits(self):
        """
        Tests retrieval of hits
        """

        from flask_monitoringdashboard.database.host import get_host_hits
        from flask_monitoringdashboard.database.request import add_request
        with session_scope() as db_session:
            current_hits = get_host_hits(db_session)
            add_request(db_session, 1, 0, 0, '')
            new_hit = [hit for hit in get_host_hits(db_session) if hit not in current_hits]
            self.assertEqual(len(new_hit), 1)
            host_id, hits = new_hit[0]
            self.assertEqual(hits, 1)
            self.assertEqual(host_id, 0)
