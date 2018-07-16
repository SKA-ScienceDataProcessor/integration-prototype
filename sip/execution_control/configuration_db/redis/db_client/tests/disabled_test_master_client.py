# -*- coding: utf-8 -*-
"""Unit tests for the master controller client.

***************************************************************************
FIXME(BM): I've disabled these tests as they need to be rewritten to not
fail depending on the order they are run or commands in __main__!
**************************************************************************

# A sample schema, like what we'd get from json.load()
schema = {
    "type": "object",
    "properties": {
        "price": {"type": "number"},
        "name": {"type": "string"},
    },
}

# if no exception is raised by validate(), the instance is valid.
validate({'name': "myname", "price": 34.99}, schema)
"""

import logging
import sys
import unittest

import redis

from ..master_client import MasterDbClient
from ..utils.set_initial_data import main as init_db


class DbClientTests(unittest.TestCase):
    """Unit tests of the Master Controller Configuration database client."""

    def setUp(self):
        """Execute before each test."""
        self._db = MasterDbClient()
        self._log = logging.getLogger("DbClientTests.testPath")

    def tearDown(self):
        """Execute after each test."""

    def test_set_state(self):
        """TODO test description."""
        name = ['execution_control', 'master_controller']
        field = 'SDP_state'
        value = "running"
        self._db.update_value(name, field, value)
        sdp_state_v = self._db.get_value(name, field)
        self.assertEqual(sdp_state_v, "running")

    def test_get_state(self):
        """TODO test description."""
        name = ['execution_control', 'master_controller']
        field = 'TANGO_state'
        tango_state_v = self._db.get_value(name, field)
        self.assertEqual(tango_state_v, 'ON')

    def test_get_all_states(self):
        """TODO test description."""
        name = ['execution_control', 'master_controller']
        values = self._db.get_all_value(name)
        self.assertNotEqual(values, None)

    def test_add_to_list(self):
        """TODO test description."""
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        service = {'name': 'sdp_services.data_queue', 'enabled': 'False'}
        self._db.add_service_to_list(service_list_name, service)
        element = self._db.get_service_from_list(service_list_name, 0)
        self.assertEqual(element['name'], 'sdp_services.data_queue')
        # Value in string
        self.assertEqual(element['enabled'], 'False')

    def test_length(self):
        """TODO test description."""
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        self.assertEqual(self._db.get_service_list_length(service_list_name),
                         6)

    def test_list_access(self):
        """TODO test description."""
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        element = self._db.get_service_from_list(service_list_name, 0)
        self.assertEqual(element['name'], 'sdp_services.data_queue')
        element = self._db.get_service_from_list(service_list_name, 1)
        self.assertEqual(element['name'], 'sdp_services.local_sky_model')

    def test_path(self):
        """TODO test description."""
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        element = self._db.get_service_from_list(service_list_name, 0)
        # log.debug(element['name'])
        field = 'state'
        value = "stopped"
        self._db.update_service(element['name'], field, value)
        service_name = ['sdp_services', 'data_queue']
        service = self._db.get_value(service_name, field)
        self.assertEqual(service, 'stopped')

    def test_boolean(self):
        """TODO test description."""
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        element = self._db.get_service_from_list_bool(service_list_name, 0)
        self.assertTrue(element['enabled'], False)


if __name__ == '__main__':
    # Delete all the data in the database
    DB_CLIENT = redis.Redis()
    DB_CLIENT.flushdb()

    # Populates the database with initial data
    init_db()

    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("SIP.EC.CBD.tests").setLevel(logging.DEBUG)
    unittest.main()
