# -*- coding: utf-8 -*-
"""Unit tests for the configuration database mock API
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

import unittest
import logging
import sys
from master_client import masterClient

db = masterClient()
name = ['execution_control', 'master_controller']
field = 'SDP_state'
value = db.get_value(name, field)
service_list_name = ['execution_control', 'master_controller',
                     'service_list']
# element = db.get_service_from_list(service_list_name, 0)
# print(element['enabled'])
# print(type(element['enabled']))
#
# new = bool(element['enabled'])
# print(new)
# print(type(new))

# new_element = db.get_service_from_list_bool(service_list_name, 0)
# print(new_element['enabled'])
# test = new_element['enabled']
# print(type(test))

#
# for e in new_element:
#     print(type(new_element[e]))

class DbClientTests(unittest.TestCase):
    def setUp(self):
        self._db = masterClient()
        self._log = logging.getLogger("DbClientTests.testPath")

    def tearDown(self):
        """Executed after each test."""
        #TODO: (NJT) Need to flushall the and run the python script
        pass

    def testSetState(self):
        name = ['execution_control', 'master_controller']
        field = 'SDP_state'
        value = "running"
        self._db.update_state(name, field, value)
        SDP_state_v = self._db.get_value(name, field)
        self.assertEqual(SDP_state_v, "running")

    def testGetState(self):
        name = ['execution_control', 'master_controller']
        field = 'TANGO_state'
        TANGO_state_v = self._db.get_value(name, field)
        self.assertEqual(TANGO_state_v, 'ON')

    def testGetAllState(self):
        name = ['execution_control', 'master_controller']
        all = self._db.get_value_all(name)
        self.assertNotEqual(all, None)

    def testAddList(self):
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        dict = {
                  'name': 'sdp_services.data_queue',
                  'enabled': 'False'
               }
        self._db.add_service_to_list(service_list_name, dict)
        element = self._db.get_service_from_list(service_list_name, 0)
        self.assertEqual(element['name'],
                'sdp_services.data_queue')
        # Value in string
        self.assertEqual(element['enabled'], 'False')

    def testLength(self):
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        self.assertEqual(self._db.get_service_list_length(service_list_name), 6)

    def testListAccess(self):
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        element = self._db.get_service_from_list(service_list_name, 0)
        self.assertEqual(element['name'],
                'sdp_services.data_queue')
        element = self._db.get_service_from_list(service_list_name, 1)
        self.assertEqual(element['name'],
                'sdp_services.local_sky_model')

    def testPath(self):
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

    #TODO: (NJT) Get this working. Important
    def testBoolean(self):
        service_list_name = ['execution_control', 'master_controller',
                             'service_list']
        element = self._db.get_service_from_list_bool(service_list_name, 0)
        new_value = element['enabled']
        self.assertTrue(element['enabled'], False)

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger("DbClientTests.testPath").setLevel(logging.DEBUG)
    unittest.main()
